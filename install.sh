#!/bin/bash
#
# Installation pour Raspberry Pi CMz !
#
echo "Déplacer les dossiers"
sudo mv /home/pi/IntercomPi/Projet /home/pi/Projet
sudo mv /home/pi/IntercomPi/ScriptsDemarrage /home/pi/ScriptsDemarrage
sudo mv /home/pi/IntercomPi/systemconfig /home/pi/systemconfig
sudo mv /home/pi/IntercomPi/install.sh /home/pi/install.sh
sudo rm -R /home/pi/IntercomPi

echo "Installation des paquets APT ..."

sudo apt update
sudo apt install -y jackd
sudo apt install -y jack-capture
sudo apt install -y python3-full
sudo apt install -y python3-venv
sudo apt install -y python3-socketio
sudo apt install -y python3-rpi.gpio
sudo apt install -y python3-netifaces
sudo apt install -y python3-rtmidi
sudo apt install -y python3-jack-client
sudo apt install -y python3-soundfile
sudo apt install -y python3-numpy
sudo apt install -y swh-lv2
sudo apt install -y git
sudo apt install -y python3-pip
sudo apt install -y curl
sudo apt install -y pmount
sudo apt install -y lilv-utils
echo "Installation APT complète !"

echo "Installation de Companion ... "
sudo curl https://raw.githubusercontent.com/bitfocus/companion-pi/main/install.sh | sudo bash
echo "Installation de Companion complète ! "

echo "Installation de raveloxmidi pour RTP Midi Apple"
sudo apt install -y git pkg-config libasound2-dev libavahi-client-dev autoconf automake
mkdir Driver
cd Driver
git clone -b experimental https://github.com/ravelox/pimidi.git
cd pimidi/raveloxmidi/ && ./autogen.sh && ./configure && make -j2
sudo make install
cd
echo "Installation de raveloxmidi complète."


echo "Installation de l'environnement Python et ses modules dans /home/pi/EnvPython ... "
python3 -m venv --system-site-packages EnvPython
activate () {
  . ../EnvPython/bin/activate
}
which pip
/home/pi/EnvPython/bin/pip install psutil
/home/pi/EnvPython/bin/pip install board
/home/pi/EnvPython/bin/pip install pillow
/home/pi/EnvPython/bin/pip install adafruit-blinka
/home/pi/EnvPython/bin/pip install adafruit-circuitpython-ssd1306
/home/pi/EnvPython/bin/pip install adafruit-io
/home/pi/EnvPython/bin/pip install argparse
/home/pi/EnvPython/bin/pip install numpy
/home/pi/EnvPython/bin/pip install mido
echo "Installation Python complète !"

echo "Téléchargement Driver AES-67 ... "
cd Driver
git clone https://github.com/bondagit/aes67-linux-daemon.git
cd aes67-linux-daemon
echo "Téléchargement des dépendances du Driver ... "
sh ubuntu-packages.sh

echo "Compilation du module Alsa, du daemon et WebUI AES-67 ... "
#Compilation avec Daemon option -DWITHSYSTEMD=ON (copie du build.sh)

# Tested on Ubuntu 18.04
#

#we need clang when compiling on ARMv7
export CC=/usr/bin/clang
export CXX=/usr/bin/clang++

TOPDIR=$(pwd)

cd 3rdparty
if [ ! -d ravenna-alsa-lkm ]; then
  git clone --single-branch --branch aes67-daemon https://github.com/bondagit/ravenna-alsa-lkm.git
  cd ravenna-alsa-lkm/driver
  make
  cd ../..
fi

if [ ! -d cpp-httplib ]; then
  git clone https://github.com/bondagit/cpp-httplib.git
  cd cpp-httplib
  git checkout 42f9f9107f87ad2ee04be117dbbadd621c449552
  cd ..
fi
cd ..

cd webui
if  [ -f webui.tar.gz ]; then
  rm -f webui.tar.gz
fi
echo "Downloading current webui release ..."
wget https://github.com/bondagit/aes67-linux-daemon/releases/latest/download/webui.tar.gz
if [ -f webui.tar.gz ]; then
  tar -xzvf webui.tar.gz
else
  echo "Building and installing webui ..."
  # npm install react-modal react-toastify react-router-dom
  npm install
  npm run build
fi
cd ..

cd daemon
echo "Building aes67-daemon ..."
cmake -DCPP_HTTPLIB_DIR="$TOPDIR"/3rdparty/cpp-httplib -DRAVENNA_ALSA_LKM_DIR="$TOPDIR"/3rdparty/ravenna-alsa-lkm -DENABLE_TESTS=ON -DWITH_AVAHI=ON -DFAKE_DRIVER=OFF -DWITH_SYSTEMD=ON .
make
cd ..

echo "Fin de la compilation"

echo "Installation d'un service systemd"
cd systemd
sudo ./install.sh
cd
echo "VAD AES-67 Installée ! Lancer la carte son avec ScriptsDemarrage/demarrage-aes67.sh ..."
echo "Faire un 'crontab -e' et ajouter '@reboot /home/pi/ScriptsDemarrage/demarrage-aes67.sh' pour un demarrage automatique"


echo "Charger le module VirMidi pour créer des ports midi peripheriques virtuel"
echo "snd_virmidi" | sudo tee -a /etc/modules
echo "snd_virmidi Chargé"

echo "Activer i2c sur le Raspberry"
sudo raspi-config nonint do_i2c 0
echo "i2c pour écran oled activé !"

echo "Modification des droits des services"
chown -R pi /home/pi/systemconfig
sudo chmod -R 644 /home/pi/systemconfig

echo "Préparation des services Ecran, Gpio, RTPMidi, demarrage AES-67 pour systemd"
sudo cp /home/pi/systemconfig/ecran-oled.service /etc/systemd/system/ecran-oled.service
sudo cp /home/pi/systemconfig/gpio-to-midi.service /etc/systemd/system/gpio-to-midi.service
sudo cp /home/pi/systemconfig/tcp-to-gpio.service /etc/systemd/system/tcp-to-gpio.service
sudo cp /home/pi/systemconfig/raveloxmidi.conf /etc/raveloxmidi.conf
sudo cp /home/pi/systemconfig/raveloxmidi.service /etc/systemd/system/raveloxmidi.service
sudo cp /home/pi/systemconfig/demarrage-aes67.service /etc/systemd/system/demarrage-aes67.service
sudo rm -R /home/pi/systemconfig

echo "Modification des droits des Projets et scripts"
chown -R pi /home/pi/Projet
chown -R pi /home/pi/ScriptsDemarrage
chmod -R 755 /home/pi/Projet
chmod -R 755 /home/pi/ScriptsDemarrage

echo "Activation au démarrage et lancement des services "
sudo systemctl daemon-reload
sudo systemctl enable ecran-oled
sudo systemctl enable gpio-to-midi
sudo systemctl enable tcp-to-gpio
sudo systemctl enable raveloxmidi
sudo systemctl enable demarrage-aes67
sudo systemctl start ecran-oled
sudo systemctl start gpio-to-midi
sudo systemctl start tcp-to-gpio
sudo systemctl start raveloxmidi
sudo systemctl start demarrage-aes67
echo "Services systemd actifs"

rm install.sh

echo "Fin de l'installation"
exit
