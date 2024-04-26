import subprocess
import time
import socket
import sys

# Fonction pour vérifier si jackd est en cours d'exécution
def check_jackd():
    if subprocess.call(["pgrep", "-x", "jackd"]) != 0:
        print("Erreur: jackd n'est pas en cours d'exécution.")
        exit(1)

# Fonction pour lancer les trois instances de Jalv
def launch_jalv_instances():
    delays = ["Delay1", "Delay2", "Delay3"]
    for delay in delays:
        subprocess.Popen(["jalv", "-n", delay, "-c", "delay_time=1", "-i", "http://plugin.org.uk/swh-plugins/delay_c"])

# Fonction pour établir les connexions Jack nécessaires
def establish_jack_connections():
    time.sleep(2)  # Attente pour laisser le temps aux instances Jalv de démarrer
    subprocess.call(["jack_connect", "system:capture_1", "Delay1:in"])
    subprocess.call(["jack_connect", "Delay1:out", "Delay2:in"])
    subprocess.call(["jack_connect", "Delay2:out", "Delay3:in"])
    subprocess.call(["jack_connect", "Delay3:out", "system:playback_1"])

# Fonction pour afficher
def send_tcp_info(*args):
    try:
        # Assemblage de la chaîne de caractères
        data = ' '.join(map(str, args))

        # Créer un socket TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Se connecter au serveur distant (127.0.0.1:7003)
            s.connect(('127.0.0.1', 7003))
            # Envoi des données
            s.sendall(data.encode())
            print("Données envoyées :", data)
    except KeyboardInterrupt:
        raise KeyboardInterrupt  # Propage l'interruption au clavier
    except Exception as e:
        print("Une erreur s'est produite :", e)

# Récupérer la variable passée en argument
if len(sys.argv) < 2:
    print("Usage: ./script.py <variable>")
    sys.exit(1)

variable = sys.argv[1]

# Utiliser la variable comme bon vous semble, par exemple l'imprimer
# print("La variable est:", variable)

# Utiliser la variable pour décider des actions à effectuer

if variable == "start":
    # Ajoutez ici le code pour démarrer votre fonction
    print("Démarrage de la fonction...")
    # Vérifie si jackd est en cours d'exécution
    check_jackd()
    # Lance les trois instances de Jalv
    launch_jalv_instances()
    # Etablir les connexions dans Jack
    establish_jack_connections()
    # Donner les infos à l'ecran :
    send_tcp_info("info3_$Boucle Jack :$$capture_1 -> playback_1$")
elif variable == "stop":
    # Ajoutez ici le code pour arrêter votre fonction
    print("Arrêt de la fonction...")
    subprocess.run(["killall", "jalv"])
    send_tcp_info("info3_$$           ...Not Running...$$")
else:
    print("La variable doit être 'start' ou 'stop'")


