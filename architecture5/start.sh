#!/bin/sh
if [ -z "$1" ]
  then
    echo "Please put your RDS endpoint"
    exit 1
elif [ -z "$2" ]
  then
    echo "Please put ACCESS KEY"
    exit 1
elif [ -z "$3" ]
  then
    echo "Please put your SECRET KEY"
    exit 1
elif [ -z "$4" ]
  then
    echo "Please put your S3 region"
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
sudo systemctl stop aws_app
sudo service nginx stop
sed -i "s/<YOUR_RDS_ENDPOINT>/$1/" views.py
sed -i "s/<YOUR_ACCESS_KEY>/$2/" views.py
sed -i "s/<YOUR_SECRET_ACCESS_KEY>/$3/" views.py
sed -i "s/<YOUR_REGION>/$4/" views.py
sudo rm -r /etc/nginx/sites-enabled/aws_app_nginx.conf
sudo rm -r /etc/systemd/system/aws_app.service
sudo ln -s /home/ubuntu/uis_aws/architecture5/aws_app_nginx.conf /etc/nginx/sites-enabled
sudo ln -s /home/ubuntu/uis_aws/architecture5/aws_app.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl start aws_app
sudo service nginx start
