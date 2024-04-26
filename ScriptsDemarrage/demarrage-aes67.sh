#!/bin/bash

# Chemin vers le module
module_path="/home/pi/Driver/aes67-linux-daemon/3rdparty/ravenna-alsa-lkm/driver"
module_name="MergingRavennaALSA.ko"

# Charger le module avec sudo insmod
echo "Chargement du module..."
sudo insmod "$module_path/$module_name"

# Attente jusqu'à ce que le module soit chargé
while ! lsmod | grep -q "MergingRavennaALSA"; do
    sleep 1
done

echo "Module chargé avec succès."

# Lancer le service avec systemd
echo "Lancement du service..."
sudo systemctl start aes67-daemon.service

# Attente jusqu'à ce que le service soit démarré
while ! systemctl is-active --quiet aes67-daemon.service; do
    sleep 1
done

echo "Service démarré avec succès."

# Quitter le script
echo "Tâches terminées. Quitter le script."
