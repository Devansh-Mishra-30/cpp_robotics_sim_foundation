$ErrorActionPreference = "Stop"

Write-Host "Configuring project..."
cmake -S . -B build

Write-Host "Building project..."
cmake --build build

Write-Host "Running executable..."
.\build\Debug\robotics_sim.exe
