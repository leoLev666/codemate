@echo off
chcp 65001 >nul
echo ========================================
echo   Codemate 后端服务
echo ========================================
echo.
echo 启动地址: http://localhost:8001
echo API 文档: http://localhost:8001/docs
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

G:\Anaconda\envs\codemate_project\Scripts\python.exe -m uvicorn src.backend.main:create_app --factory --host 0.0.0.0 --port 8001 --reload
pause
