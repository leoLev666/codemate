@echo off
chcp 65001 >nul
echo ========================================
echo   Codemate 前端界面
echo ========================================
echo.
echo 打开浏览器访问: http://localhost:8501
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

G:\Anaconda\envs\codemate_project\Scripts\python.exe -m streamlit run src/frontend/app.py
pause
