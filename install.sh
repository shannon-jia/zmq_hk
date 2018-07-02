#!/bin/sh

echo "install zmq-hk to /usr/local/sam-pub..."
sudo cp zmq-hk /usr/local/sam-pub
echo "install zmq-hk.conf to /etc/init for upstart..."
sudo cp zmq-hk.conf /etc/init
echo "finish"
echo "Start Job use command: "
echo "    sudo start zmq-hk "
echo "GoodLuck ;)"

