# IntercomPi

Utiliser un Raspberry Pi 4B dans un environnement broadcast avec diverses fonctions associees aux GPIO et divers acces depuis Companion

# Contexte
### SOFTWARE :
Systeme officiel Raspberry Pi Os Lite 64
Programmation des scripts en python dans un environnement virtuel
Automatismes du systeme via systemd

### HARDWARE :

HAT Poe Waveshare

GPIO via Opto-Coupleurs :
4x GPIO-in : 22, 23, 24, 25
4x GPIO-out : 19, 

Ecran Oled 128x32 i2c pour debug :
GPIO 2 : Sda
GPIO 3 : Scl

Carte son USB Audio Class compliant :

Carte son Ravenna / AES67 sur eth0

# Fonctions

### GPIO-to-Midi : 
Envoi de notes Midi depuis les 4x GPIO-in vers local et reseau compatible RTP Midi Apple. Decodeur 4>16 bits

### TCP-to-GPIO : 
Commutation des 4x GPIO-out par des commandes TCP. Commandes incluses dans Companion. Encodeur 16>4 bits

### Ecran Oled : 
Affichage alternatif
  - Adresses IP wlan0 et eth0
  - gpio-to-midi
  - tcp-to-gpio
  - multi-fx audio
  - repondeur audio
  - reserve Companion
  - Standby

### Fonctions audio via Jackd :
  - Multi-Fx commutable avec : Delay 3s / Reverb / Pitch High / Pitch Low
  - Repondeur Audio depuis commandes Midi (GPIO in) avec Annonce d'accueil, Enregistrement des messages, relecture, Suppressions des enregistrements

### Companion :
  - Menu d'acces aux differentes pages
  - Gestion des scripts de lancement jackd et Fonctions audio
  - Gestion des interfaces reseau
  - Acces au RTP Midi Apple
  - Acces au Repondeur
  - Page 15 touches > 4 GPIO via encodeur 16>4


# Installation
  Recuperation du depot :
  
    git clone https://github.com/CMZrasprojects/IntercomPi.git

  Lancer le script d'installation :
  
    /bin/bash install.sh

  Charger la config Companion :

    Ouvrir la page web et "import" le fichier IntercomPi.companionconfig
