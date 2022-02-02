# ensure the CWD is the directory of this script
script_dir="$(dirname $(realpath $0))"
cd $script_dir
cd ../  # main directory

num=$(pgrep -f gunicorn | wc -l)
if [ $num -gt 0 ]
then
  echo "Gunicorn is running."
else
  echo "Not running. Reloaded"
fi