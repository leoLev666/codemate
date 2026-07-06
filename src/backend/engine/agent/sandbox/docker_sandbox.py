"""Docker 沙箱 —— 安全的代码执行环境。

用户提交的 Python 代码在一个隔离的 Docker 容器中运行，
具备以下安全措施：
  - network_mode="none"    → 无网络访问
  - read_only=True          → 根文件系统只读
  - cap_drop=["ALL"]        → 移除所有 Linux capabilities
  - security_opt            → 禁止提权
  - mem_limit               → 内存限制
  - timeout                 → 执行超时
  - remove=True             → 执行完自动销毁容器

与旧代码的关键区别：
  旧代码用 subprocess.run 在宿主机直接执行，六关键字黑名单一秒可绕过。
  新代码用 Docker 容器隔离，即使代码恶意也无法影响宿主机。
"""

import asyncio

import docker
from docker.errors import DockerException, NotFound
from docker.models.containers import Container

from src.backend.config import Settings
from src.backend.engine.agent.tool_registry import ToolResult


class DockerSandbox:
    """在隔离的 Docker 容器中执行 Python 代码。"""

    def __init__(self, settings: Settings):
        self._settings = settings
        try:
            self._client = docker.from_env()
        except DockerException as e:
            raise RuntimeError(
                "Docker 不可用，请确保 Docker Desktop 正在运行。"
            ) from e
        self._image = settings.DOCKER_SANDBOX_IMAGE
        self._timeout = settings.SANDBOX_TIMEOUT
        self._memory = settings.SANDBOX_MEMORY_LIMIT

    async def execute(self, code: str) -> ToolResult:
        """在沙箱容器中运行 Python 代码。

        Args:
            code: 要执行的 Python 源码。

        Returns:
            ToolResult，含 stdout/stderr 和退出信息。
        """
        try:
            container: Container = self._client.containers.run(
                image=self._image,
                command=["python", "-c", code],
                detach=True,
                mem_limit=self._memory,
                network_mode="none",          # 无网络
                read_only=True,               # 只读文件系统
                cap_drop=["ALL"],             # 移除所有内核能力
                security_opt=["no-new-privileges:true"],  # 禁止提权
                tmpfs={"/tmp": "size=64m"},   # 仅 /tmp 可写
                remove=True,                  # 执行完自动删除
            )
        except docker.errors.ImageNotFound:
            return ToolResult(
                output="",
                error=(
                    f"Docker 镜像 '{self._image}' 不存在。"
                    f"请先构建: docker build -f docker/sandbox.Dockerfile "
                    f"-t {self._image} ."
                ),
            )

        try:
            # 等待容器执行完成（带超时）
            exit_info = await asyncio.get_event_loop().run_in_executor(
                None, lambda: container.wait(timeout=self._timeout)
            )
            logs = container.logs(stdout=True, stderr=True)
            output = logs.decode("utf-8", errors="replace")

            exit_code = exit_info.get("StatusCode", -1) if exit_info else -1

            if exit_code == 0:
                return ToolResult(output=output.strip() or "(无输出)")
            else:
                return ToolResult(output="", error=output.strip())
        except Exception:
            # 超时或其他异常 → 强制终止并清理容器
            try:
                container.kill()
                container.remove(force=True)
            except Exception:
                pass
            return ToolResult(
                output="",
                error=f"代码执行超时（>{self._timeout}秒）",
            )
