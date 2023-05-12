#!/bin/sh

# create new repository
mkdir lingfo_temp
cd lingfo_temp

git init
mv .git .lingfo-git

cd ..

# and put the repository to library dir
cp -r lingfo_temp/.lingfo-git $1/
rm -rf lingfo_temp/ 

cd $1/

echo '.lingfo-git/*' >> .gitignore
git --git-dir=.lingfo-git add .
git --git-dir=.lingfo-git commit -m "Lingfo"