#!/bin/sh
sudo apt-get update
sudo apt-get install build-essential python
sudo apt-get install python-setuptools
sudo apt-get install mysql-server
sudo apt-get install python-dev
sudo apt-get install nginx
sudo apt-get install upstart
sudo /etc/init.d/nginx start
sudo ln -s /home/ubuntu/uis_aws/architecture0/aws_app_nginx.conf /etc/nginx/sites-enabled
sudo ln -s /home/ubuntu/uis_aws/architecture0/aws_app.service /etc/systemd/system
mysql_secure_installation
sudo easy_install pip
sudo pip install virtualenv
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
