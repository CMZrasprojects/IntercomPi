#!/bin/bash


# Définition de l'environnement
export PATH="/usr/bin:/bin:/usr/sbin:/sbin"

# Nom du périphérique audio à rechercher
device_name="USB Audio Device"

# Recherche du numéro de carte et de périphérique audio par son nom
device_info=$(aplay -l | grep "$device_name" | head -n 1)
device_number=$(echo "$device_info" | awk '{print $2}' | sed 's/://')
device_subdevice=0  # Nous utilisons 0 par défaut, mais vous pouvez ajuster si nécessaire

# Vérifier si jackd est déjà en cours d'exécution
if pgrep -x "jackd" > /dev/null; then
    echo "jackd est déjà en cours d'exécution."
    exit 1
fi

# Vérifier si le périphérique audio a été trouvé
if [ -z "$device_info" ]; then
    echo "Périphérique audio $device_name non trouvé."
    exit 1
fi

# Démarrer jackd avec les paramètres appropriés
/usr/bin/jackd -d alsa --device hw:$device_number,$device_subdevice --rate 48000 --period 256 &

# Démarrer directement sans la recherche :
#/usr/bin/jackd -d alsa --device hw:1,0 --rate 48000 --period 256 &
