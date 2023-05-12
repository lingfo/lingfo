# create new repository
mkdir lingfo_temp
Set-Location lingfo_temp

git init
Move-Item .git .lingfo-git

Set-Location ..

# and put the repository to library dir
Copy-Item -r lingfo_temp/.lingfo-git lib/
Remove-Item -LiteralPath "lingfo_temp/" -Force -Recurse

Set-Location lib/

Write-Output '.lingfo-git/*' >> .gitignore
git --git-dir=.lingfo-git add .
git --git-dir=.lingfo-git commit -m "Lingfo"