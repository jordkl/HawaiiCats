#!/bin/bash

# Function to show usage
show_usage() {
    echo "Usage: ./git-sync.sh [push|pull] [branch]"
    echo "Example: ./git-sync.sh push main"
    echo "         ./git-sync.sh pull main"
    echo "If branch is not specified, 'main' will be used"
}

# Check if at least one argument is provided
if [ $# -lt 1 ]; then
    show_usage
    exit 1
fi

# Set the action (push or pull)
ACTION=$1

# Set the branch (default to main if not specified)
BRANCH=${2:-main}

# Set up the SSH command to use the correct key
export GIT_SSH_COMMAND="ssh -i /home/flask/.ssh/github_deploy"

# Execute the requested action
case $ACTION in
    push)
        echo "Pushing to branch: $BRANCH"
        git push origin $BRANCH
        ;;
    pull)
        echo "Pulling from branch: $BRANCH"
        git pull origin $BRANCH
        ;;
    *)
        echo "Error: Invalid action. Use 'push' or 'pull'"
        show_usage
        exit 1
        ;;
esac
