#!/bin/bash

git_user=tnn4
git_repo=reddit-bot-starter
remote_repo=https://github.com/$git_user/$git_repo.git

main() {
    # place stuff you want to run here
    echo "initializing git repo: !"
    git init
    git remote add origin $remote_repo
    git branch -M main
    git add .
    git commit -m 'init'
    git push -u origin main
}

main
