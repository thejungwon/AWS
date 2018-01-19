#!/bin/sh
sudo apt-get --yes update
sudo apt-get --yes install build-essential python
sudo apt-get --yes install python-setuptools
echo "mysql-server-5.6 mysql-server/root_password password uisaws123" | sudo debconf-set-selections
echo "mysql-server-5.6 mysql-server/root_password_again password uisaws123" | sudo debconf-set-selections
sudo apt-get --yes install mysql-server
sudo apt-get --yes install python-dev
sudo apt-get --yes install nginx
sudo apt-get --yes install upstart
mysql -u root --password=uisaws123 < earthquake.sql
sudo /etc/init.d/nginx start
sudo easy_install pip
sudo pip install virtualenv
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
deactivate
python nginx_conf_maker.py
sudo ln -s /home/ubuntu/uis_aws/architecture0/aws_app_nginx.conf /etc/nginx/sites-enabled
sudo ln -s /home/ubuntu/uis_aws/architecture0/aws_app.service /etc/systemd/system
sudo systemctl start aws_app
sudo systemctl start nginx
