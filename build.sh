#!/bin/sh
echo "Build exec file in pyinstaller..."
rm -rf dist build
pyinstaller -F zmq_hk-cli.py -n zmq-hk
cp zmq-hk.conf dist
cp install.sh dist
echo "                   "
echo " ************ Finished ************"
echo " Exec file is dist/zmq-hk, please check it."
