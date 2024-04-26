#!/bin/bash

# Vérifier si jackd est en cours d'exécution
if pgrep -x "jackd" > /dev/null
then
    echo "Arrêt de jackd..."
    pkill jackd
    echo "jackd arrêté avec succès."
else
    echo "jackd n'est pas en cours d'exécution."
fi
