@echo off
REM Flutter运行脚本 - 带日志过滤
REM 只显示flutter相关的重要日志

echo 启动Flutter应用（清洁日志模式）...
echo.

REM 运行flutter，过滤掉无关日志
flutter run 2>&1 | findstr /V /C:"Skipped" /C:"RtgSched" /C:"BufferQueue" /C:"SurfaceView" /C:"OpenGLRenderer" /C:"ViewRootImpl" /C:"HiTouch" /C:"Choreographer" /C:"InputMethodManager" /C:"DecorView" /C:"InsetsController"

pause

