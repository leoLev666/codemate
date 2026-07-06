#!/bin/bash
# Codemate 前端启动脚本
# 在 Git Bash 中运行: bash start_frontend.sh

PYTHON=/g/Anaconda/envs/codemate_project/Scripts/python.exe

echo "========================================"
echo "  Codemate 前端界面"
echo "========================================"
echo ""
echo "打开浏览器访问: http://localhost:8501"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

$PYTHON -m streamlit run src/frontend/app.py
