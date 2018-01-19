#!/bin/sh
sudo apt-get --yes update
sudo apt-get --yes install build-essential python
sudo apt-get --yes install python-setuptools
sudo debconf-set-selections <<< 'mysql-server mysql-server/uisaws123 password uisaws123'
sudo debconf-set-selections <<< 'mysql-server mysql-server/uisaws123 password uisaws123'
sudo apt-get --yes install mysql-server
sudo apt-get --yes install python-dev
sudo apt-get --yes install nginx
sudo apt-get --yes install upstart
sudo /etc/init.d/nginx start
sudo ln -s /home/ubuntu/uis_aws/architecture0/aws_app_nginx.conf /etc/nginx/sites-enabled
sudo ln -s /home/ubuntu/uis_aws/architecture0/aws_app.service /etc/systemd/system
sudo easy_install pip
sudo pip install virtualenv
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
sudo systemctl start aws_app
sudo systemctl start nginx
