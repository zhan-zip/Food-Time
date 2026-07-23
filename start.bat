@echo off
chcp 65001 >nul
title 食光记 - 开发服务器

echo ============================================
echo   食光记 Food-Time
echo   正在启动前后端服务...
echo ============================================
echo.

cd /d "%~dp0"

:: 启动后端
echo [1/2] 启动后端 API 服务 (http://localhost:8000)...
start "食光记-后端" cmd /c "cd /d server && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"
echo       后端启动中，请稍候...

:: 等待后端初始化（MySQL连接+种子数据）
echo       等待数据库初始化...
timeout /t 5 /nobreak >nul

:: 启动前端
echo [2/2] 启动前端开发服务器 (http://localhost:5173)...
start "食光记-前端" cmd /c "cd /d client && npm run dev"

echo.
echo ============================================
echo   启动完成！
echo   前端地址: http://localhost:5173
echo   后端文档: http://localhost:8000/docs
echo ============================================
echo.
echo   关闭方式：
echo   - 分别关闭"食光记-后端"和"食光记-前端"窗口
echo   - 或直接关闭本窗口（子窗口不会自动关闭）
echo.
pause
