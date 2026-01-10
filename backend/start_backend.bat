@echo off
REM Batch script to start PolicyLens backend with MongoDB Atlas connection

set MONGODB_URI=mongodb+srv://gaurav2921singh_db_user:0LWiCzxExxUU4BC3@policydrift.slmbmvv.mongodb.net/
set MONGODB_DB=policylens

echo Starting PolicyLens Backend...
echo MongoDB URI: %MONGODB_URI%
echo Database: %MONGODB_DB%
echo.

python main.py
