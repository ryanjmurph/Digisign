## Github Collaborative Development

Git Commands Cheat Sheet https://education.github.com/git-cheat-sheet-education.pdf

Steps when developing
1. Create a new branch by running `git branch <functionality name>` e.g `git branch login-functionality` 
2. Develop on your branch and once ready, commit the update set. I tend to commit each incremental change that worked. `git add .` to add the untracked files followed by `git commit -m "<messages about your commit>"` e,g `git commit -m "Added the login page"` 
3. Once you've finished working on a branch and are ready to share it with the rest, update the main branch to ensure you're up to date with any of the latest changes from other team members. `git fetch origin/main` then merge the main branch into your branch to check for any conflicts. (while in your custom branch) `git merge main`
4. Add a commit message to the merge request locally. Git will prompt you to do this.
5. Once you've sorted any merge conflicts, push the local branch to the repo `git push -u origin <branch-name>`
6. Merge the main branch on github to main by logging into Github, accessing the repo, heading over to the pull requests tab and creating a new pull request from your custom branch to main. 
7. Github will check for any conflicts as a final check and indicate whether a merge is possible. If it is, go ahead and merge the PR. If it isn't, fix any merge conflicts and complete the PR.
8. Once you've completed a PR, go back to your local environment and fetch the latest update. Switch to the main branch `git checkout main` and pull the latest changes `git pull main`. You may then go ahead and delete the custom branch `git branch -d <branch_name>`

## Usefull Git commands
```shell
git status // check which branch you're one
git branch <name> // create a new branch
git checkout <name> // switch to a different branch
git merge <name> // while in a current branch, merge another branch into the current branch
git pull <upstream>/<branch> // get the latest changes from the repo online. upstream tends to be called origin by default
git add . // add all untracked files to be tracked by git (ensure you make use of .gitignore to not track certain files such as images and generated code)
git add <name> // add a specific file to be tracked 

git reset // reset changes to a repo to the last commit
git reset --hard // force reset a branch to the last commit
git reset --hard origin/main //force reset a branch to the last commit on the online repo

git branch -d <name> // delete a specific branch
```
