#!/bin/bash
sudo apt-get update
sudo apt-get -y upgrade

sudo useradd -m slowdown
sudo mkdir /home/slowdown/.ssh

sudo cp ./slowdown_id_rsa.pub /home/slowdown/.ssh/authorized_keys
sudo cp ./flag /home/slowdown/flag

sudo chmod 600 /home/slowdown/.ssh/authorized_keys
sudo chmod 600 /home/slowdown/flag
sudo chown slowdown:slowdown /home/slowdown/flag
sudo chown slowdown:slowdown /home/slowdown/.ssh/authorized_keys
