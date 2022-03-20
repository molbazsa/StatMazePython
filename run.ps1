param ($app="animate")

if ($app -eq "animate") {
    python .\src\main.py
} elseif ($app -eq "algorithm") {
    python .\src\random_maze.py
} else {
    Write-Host "No such app: $app"
}
