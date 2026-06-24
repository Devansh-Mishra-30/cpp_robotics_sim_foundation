$ErrorActionPreference = "Stop"

Write-Host "Removing old build folder..."
if (Test-Path "build") {
    Remove-Item -Recurse -Force build
}

Write-Host "Configuring standalone C++ project with Visual Studio 2022..."
cmake -S . -B build -G "Visual Studio 17 2022" -A x64

Write-Host "Building standalone C++ project..."
cmake --build build --config Debug

Write-Host "Running executable..."
.\build\Debug\robotics_sim.exe