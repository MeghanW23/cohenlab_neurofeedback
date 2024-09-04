
# script used to pull recent changes Drepository from github to the docker image
REPO_URL="https://github.com/MeghanW23/cohenlab_neurofeedback"

# Clone the repository if it doesn't exist
if [ ! -d "/working_dir/repo" ]; then
  git clone "$REPO_URL" /working_dir/repo
fi

# Go to the repo directory
cd /working_dir/repo

# Pull the latest changes
git pull origin main

# to keep the container running:
exec "$@"
