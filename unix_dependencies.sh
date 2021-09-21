#!/bin/sh
# On unix systems, we may need to install some additional packages.
# This list ist taken from our .github/workflows/test_and_lint.yml and is NOT updated automatically.
# Therefore you might need to install other dependencies than the ones listed here.
# If this is the case please create a new issue and iform us by creating a new issue: https://github.com/mad-lab-fau/mad-gui/issues/new
sudo apt-get update  # To get the latest package lists
sudo apt-get install -y build-essential libgl1-mesa-dev
sudo apt-get install -y libxcb-xinerama0
sudo apt-get install -y libpulse-dev
sudo apt-get install -y tk
sudo apt-get install -y libqt5gstreamer-dev
sudo apt-get install -y libgssapi-krb5-2
sudo apt-get install -y libqt5multimedia5-plugins
sudo apt-get install -y libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-pulseaudio
sudo apt-get -y install libpulse-mainloop-glib0
