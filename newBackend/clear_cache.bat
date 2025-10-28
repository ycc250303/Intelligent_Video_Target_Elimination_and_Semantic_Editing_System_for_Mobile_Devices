@echo off
echo 正在清除Python缓存...

:: 删除所有 __pycache__ 目录
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

:: 删除所有 .pyc 文件
del /s /q *.pyc 2>nul

:: 删除所有 .pyo 文件  
del /s /q *.pyo 2>nul

echo Python缓存已清除！
echo.
echo 现在请运行: python run_server.py
pause

