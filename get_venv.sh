#  gdown --no-cookies "https://drive.google.com/file/d/1tLkdwqhbE40BLnxVN37rU2ku7VlQFZEZ/view?usp=sharing" -O venv.tar.gz
tarball_path:"/workdir/venv.tar.gz"

echo "Creating python virtual environment from tarball"
if [ ! -d $tarball_path ]; then
  echo "Cannot find path to venv tarball. Attempting to pull from google drive using gdown"
  gdown --no-cookies "https://drive.google.com/file/d/1tLkdwqhbE40BLnxVN37rU2ku7VlQFZEZ/view?usp=sharing" -O venv.tar.gz
else
  tar -xzvf filename.tar.gz

