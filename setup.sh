sudo apt-get update
sudo apt-get install python3.8-venv
sudo apt install libcairo2-dev pkg-config python3-dev
pip3 install --upgrade pip

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
Pip install wheel
pip install -r requirements/full_requirements.txt

