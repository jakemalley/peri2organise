peri2organise
=============

A organisation and management tool for Frome College music department.

peri2organise aims to make organising and managing extracurricular 
peripatetic music lessons easier by providing tools to easily create 
and manage lessons, notify tutors and students and take lesson registers.

peri2organise uses flask, a Python framework, to create a web application 
for tutors and students to access over the internet, login and view 
upcoming lessons.

Created and developed by Jake Malley as part of WJEC Computing A Level

Installation
============

## Development
Download the source code.
```git clone https://github.com/jakemalley/peri2organise```
```cd peri2organise```
Install virtualenv and create a new environment.
```pip install virtualenv```
```virtualenv env```
```source env/bin/activate```
Install the requirements.
```pip install -r requirements.txt```
Run the development server.
```python manage.py runserver```

## Production
These installation instructions have been written for CentOS 7.

Install the EPEL release.
```sudo rpm -iUvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm```
Run YUM update.
```sudo yum update```
Add the YUM repository.
```
sudo tee /etc/yum.repos.d/docker.repo <<-'EOF'
[dockerrepo]
name=Docker Repository
baseurl=https://yum.dockerproject.org/repo/main/centos/$releasever/
enabled=1
gpgcheck=1
gpgkey=https://yum.dockerproject.org/gpg
EOF
```
Install docker-engine, python-pip and git.
```sudo yum install docker-engine python-pip git```
Start and enable docker.
```
sudo systemctl start docker
sudo systemctl enable docker
```
Install docker-compose.
```sudo pip install docker-compose```
Download the source code.
```git clone https://github.com/jakemalley/peri2organise```
```cd peri2organise```

Optional: Set the postgres database password.
```cd docker/```
Edit the docker-compose.yml file, edit the password on line 37.
```vim docker-compose.yml```
Create a configuration. The SMTP server settings will need to be changed, along with a few other options.
```
cd ../
cp peri2organise.conf.example peri2organise.conf
vim peri2organise.conf
```
Move to the docker folder.
```
cd docker/
sudo docker-compose build
sudo docker-compose up -d
sudo docker-compose run web /usr/local/bin/python -c "from peri2organise import db;db.create_all()"
```

Create a new admin user.
Change the new admin's username and password by editing the python file.
```
cd ../
vim setup_admin.py # Change the username / password variables at the top of this file.
sudo docker-compose stop
sudo docker-compose rm web # Enter y when asked.
sudo docker-compose build
sudo docker-compose up -d
sudo docker-compose run web /usr/local/bin/python setup_admin.py
```

The can now be accessed from the machines IP address.
