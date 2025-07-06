$BaseDir = "C:\Users\Cliente\Desktop\Satori\scripts"

Set-Location $BaseDir

Get-ChildItem -Directory | ForEach-Object {
    $dir = $_.Name
    Write-Host "Subindo projeto: $dir"

    Set-Location "$BaseDir\$dir"

    if (-Not (Test-Path ".git")) {
        git init
        git add .
        git commit -m "Commit inicial"
    }

    gh repo create $dir --public --source=. --remote=origin --push

    Write-Host "Projeto enviado: https://github.com/Leandromarcalx/$dir`n"
}

Set-Location $BaseDir