# create new repository
mkdir sushi_temp
Set-Location sushi_temp

git init
Move-Item .git .sushi-git

Set-Location ..

# and put the repository to library dir
Copy-Item -r sushi_temp/.sushi-git lib/
Remove-Item -LiteralPath "sushi_temp/" -Force -Recurse

Set-Location lib/

Write-Output '.sushi-git/*' >> .gitignore
git --git-dir=.sushi-git add .
git --git-dir=.sushi-git commit -m "Sushi"