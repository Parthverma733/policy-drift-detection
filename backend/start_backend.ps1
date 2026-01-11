# PowerShell script to start PolicyLens backend with MongoDB Atlas connection

$env:MONGODB_URI = "mongodb+srv://gaurav2921singh_db_user:0LWiCzxExxUU4BC3@policydrift.slmbmvv.mongodb.net/"
$env:MONGODB_DB = "policylens"

Write-Host "Starting PolicyLens Backend..."
Write-Host "MongoDB URI: $env:MONGODB_URI"
Write-Host "Database: $env:MONGODB_DB"
Write-Host ""

uvicorn main:app --reload

