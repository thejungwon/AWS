#!/bin/sh
if [ -z "$1" ]
  then
    echo "Please put your RDS endpoint"
    exit 1
fi
sudo apt-get --yes update
sudo apt-get --yes install build-essential python
sudo apt-get --yes install python-setuptools
sudo apt-get --yes install python-dev
sudo apt-get --yes install nginx
sudo apt-get --yes install upstart
mysql -h $1 -u root --password=uisaws123 < earthquake.sql
sudo /etc/init.d/nginx start
sudo easy_install pip
sudo pip install virtualenv
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
deactivate
python nginx_conf_maker.py
sudo systemctl stop aws_app
sudo service nginx stop
sudo rm -r /etc/nginx/sites-enabled/aws_app_nginx.conf
sudo rm -r /etc/systemd/system/aws_app.service
sudo ln -s /home/ubuntu/uis_aws/architecture1/aws_app_nginx.conf /etc/nginx/sites-enabled
sudo ln -s /home/ubuntu/uis_aws/architecture1/aws_app.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl start aws_app
sudo service nginx start
