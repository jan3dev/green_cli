```
sudo yum install git -y
sudo yum install -y python-is-python3

sudo yum install sudo wget openssl-devel -y
sudo yum groupinstall "Development Tools" -y


wget https://cmake.org/files/v3.10/cmake-3.10.0.tar.gz

tar -xvzf cmake-3.10.0.tar.gz

cd cmake-3.10.0
./bootstrap
make
sudo  make install

sudo yum -y install cargo

sudo yum -y install python-pip
/usr/bin/python3 -m pip install build

sudo yum install python3-devel
sudo yum install -y virtualenv

git clone https://github.com/jan3dev/green_cli
cd green_cli
virtualenv venv
source venv/bin/activate
pip install -r requirements-wally.txt
pip install ~/prj/jan3/gdk-python/share/python/greenaddress-0.0.65-cp39-cp39-linux_x86_64.whl
pip install requests
pip install websockets
pip install .
```
