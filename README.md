# IntercomPi

Utiliser un Raspberry Pi 4B dans un environnement broadcast avec diverses fonctions associees aux GPIO et divers acces depuis Companion

SOFTWARE :
Systeme officiel Raspberry Pi Os Lite 64
Programmation des scripts en python dans un environnement virtuel
Automatismes du systeme via systemd

HARDWARE :

HAT Poe Waveshare

GPIO via Opto-Coupleurs :
4x GPIO-in : 22, 23, 24, 25
4x GPIO-out : 19, 

Ecran Oled 128x32 i2c pour debug :
GPIO 2 : Sda
GPIO 3 : Scl

Carte son USB Audio Class compliant :

Carte son Ravenna / AES67 sur eth0

FONCTIONS SOFTWARE :
GPIO-to-Midi : Envoi de notes Midi depuis les 4x GPIO-in vers local et reseau compatible RTP Midi Apple

TCP-to-GPIO : commutation des 4x GPIO-out par des commandes TCP. Commandes incluses dans Companion

Ecran Oled : Affichage alternatif
  - Adresses IP wlan0 et eth0
  - gpio-to-midi
  - tcp-to-gpio
  - multi-fx audio
  - repondeur audio
  - reserve Companion
  - Standby


