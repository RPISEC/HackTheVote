sudo apt update
sudo apt install docker.io python3-pip ufw tmux chromium-chromedriver

sudo systemctl enable --now ufw
sudo ufw allow 8000
sudo ufw allow 22
sudo ufw enable

if [ ! "$(sudo docker ps -q -f name=redis)" ]; then
    if [ "$(sudo docker ps -aq -f status=exited -f name=redis)" ]; then
        sudo docker rm redis
    fi
    sudo docker run --name redis -p 6666:6379 -d redis
fi


pip3 install pipenv

export PATH=$PATH:$HOME/.local/bin/
cd src
pipenv install
echo 127.0.0.1 propaganda.hackthe.vote | sudo tee -a /etc/hosts
tmux \
  new-session -n "gunicorn" "pipenv run gunicorn server:app --worker-class gevent --bind 0.0.0.0:8000 -w 2" \; \
  new-window -n "huey" "pipenv run huey_consumer.py server.huey -k process -w 2" \;
