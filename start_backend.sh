#!/bin/bash
# Codemate 后端启动脚本
# 在 Git Bash 中运行: bash start_backend.sh

PYTHON=/g/Anaconda/envs/codemate_project/Scripts/python.exe

echo "========================================"
echo "  Codemate 后端服务"
echo "========================================"
echo ""
echo "启动地址: http://localhost:8001"
echo "API 文档: http://localhost:8001/docs"
echo "健康检查: http://localhost:8001/api/v1/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

$PYTHON -m uvicorn src.backend.main:create_app --factory --host 0.0.0.0 --port 8001 --reload
