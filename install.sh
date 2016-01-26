#!/bin/bash

INSTALL_DIR=$1
CLONE_RAW=https://github.com/scottidler/clone/raw/master/
CLONE_DIR=~/.clone/

# install script in /usr/local/bin unless overridden by user
sudo wget $CLONE_RAW/clone -C ${INSTALL_DIR:-/usr/local/bin/}

# install library in default clone dir location
wget $CLONE_RAW/clone.py -C $CLONE_DIR

# install config in default clone dir location
wget $CLONE_RAW/clone.cfg -C $CLONE_DIR

# fixup path to clone.py
sed -i 's|clonepy\s*=\s*.*|clonepy = ~/.clone/clone.py|g' $CLONE_DIR/clone.cfg
