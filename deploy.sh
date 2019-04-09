#!/bin/bash

eval "$(ssh-agent -s)" &&
ssh-add -k ~/.ssh/id_rsa &&
cd /home/ubuntu/EagleBackEnd
sudo git pull
source ~/.profile
sudo echo "$DOCKERHUB_PASS" | docker login --username $DOCKERHUB_USER --password-stdin 
sudo docker stop lahanku-project
sudo docker rm lahanku-project 
sudo rmi trastanechora/project_lahanku:production
sudo docker run -d --name lahanku-project -p 5000:5000 trastanechora/project_lahanku:production