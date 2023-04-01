#!/bin/sh

# create new repository
mkdir sushi_temp
cd sushi_temp

git init
mv .git .sushi-git

cd ..

# and put the repository to library dir
cp -r sushi_temp/.sushi-git $1/
rm -rf sushi_temp/ 

cd $1/

echo '.sushi-git/*' >> .gitignore
git --git-dir=.sushi-git add .
git --git-dir=.sushi-git commit -m "Sushi"