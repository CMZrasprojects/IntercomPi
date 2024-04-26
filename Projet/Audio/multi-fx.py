import subprocess
import time
import socket
import sys

# Fonction pour vérifier si jackd est en cours d'exécution
def check_jackd():
    if subprocess.call(["pgrep", "-x", "jackd"]) != 0:
        print("Erreur: jackd n'est pas en cours d'exécution.")
        exit(1)

# DELAY : Fonction pour lancer les trois instances de Jalv
def launch_jalv_delay():
    delays = ["Delay1", "Delay2", "Delay3"]
    for delay in delays:
        subprocess.Popen(["jalv", "-n", delay, "-c", "delay_time=1", "-i", "http://plugin.org.uk/swh-plugins/delay_c"])

# DELAY : Fonction pour établir les connexions Jack nécessaires
def establish_jack_connections_delay():
    time.sleep(1)  # Attente pour laisser le temps aux instances Jalv de démarrer
    subprocess.call(["jack_connect", "system:capture_1", "Delay1:in"])
    subprocess.call(["jack_connect", "Delay1:out", "Delay2:in"])
    subprocess.call(["jack_connect", "Delay2:out", "Delay3:in"])
    subprocess.call(["jack_connect", "Delay3:out", "system:playback_1"])

# REVERB : Fonction pour lancer l'instance de Jalv
    # "roomsize="      '1 to 300'   Default=75.75
    # "revtime="       '0.1 to 30'  Default=7.575
    # "damping="       '0 to 1'     Default=0.5
    # "inputbandwith=" '0 to 1'     Default=0.75
    # "drylevel="      '-70 to 0'   Default=-70
    # "earlylevel="    '-70 to 0'   Default=0.0
    # "taillevel="     '-70 to 0'   Default= -17.5
def launch_jalv_reverb():
    subprocess.Popen(["jalv", "-n", "reverb", "-c", "roomsize=150", "-c", "revtime=2.4", "-c", "damping=0.5", "-c","inputbandwith=0.4", "-c", "drylevel=0.0", "-c", "earlylevel=-25.0", "-c", "taillevel=-25.0", "-i", "http://plugin.org.uk/swh-plugins/gverb"])

# REVERB :Fonction pour établir les connexions Jack nécessaires
def establish_jack_connections_reverb():
    time.sleep(1)  # Attente pour laisser le temps aux instances Jalv de démarrer
    subprocess.call(["jack_connect", "system:capture_1", "reverb:input"])
    subprocess.call(["jack_connect", "reverb:outl", "system:playback_1"])
    subprocess.call(["jack_connect", "reverb:outr", "system:playback_2"])

# PITCH HAUT: Fonction pour lancer l'instance de Jalv ('pitch'='0.25 to 4.0')
def launch_jalv_pitch_high():
    subprocess.Popen(["jalv", "-n", "pitch", "-c", "pitch=2", "-i", "http://plugin.org.uk/swh-plugins/amPitchshift"])

# PITCH HAUT :Fonction pour établir les connexions Jack nécessaires
def establish_jack_connections_pitch_high():
    time.sleep(1)  # Attente pour laisser le temps aux instances Jalv de démarrer
    subprocess.call(["jack_connect", "system:capture_1", "pitch:input"])
    subprocess.call(["jack_connect", "pitch:output", "system:playback_1"])

# PITCH BAS : Fonction pour lancer l'instance de Jalv ('pitch'='0.25 to 4.0')
def launch_jalv_pitch_low():
    subprocess.Popen(["jalv", "-n", "pitch", "-c", "pitch=0.6", "-i", "http://plugin.org.uk/swh-plugins/amPitchshift"])

# PITCH BAS :Fonction pour établir les connexions Jack nécessaires
def establish_jack_connections_pitch_low():
    time.sleep(1)  # Attente pour laisser le temps aux instances Jalv de démarrer
    subprocess.call(["jack_connect", "system:capture_1", "pitch:input"])
    subprocess.call(["jack_connect", "pitch:output", "system:playback_1"])

def kill_all_jalv_instances():
    # Tuer tous les processus jalv en cours d'exécution
    subprocess.run(["killall", "jalv"])

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
    # Tues toutes les instance Jalv en fonction avant d'en démarrer une autre
    kill_all_jalv_instances()
    # Lance les instances en fonction de la variable :
    if len(sys.argv) > 2:
        for arg in sys.argv[2:]:
            if arg == "delay":
                launch_jalv_delay()
                establish_jack_connections_delay()
                # Donner les infos à l'ecran :
                send_tcp_info("info3_$Delay 3s :$$capture_1 -> playback_1$")
            elif arg == "reverb":
                launch_jalv_reverb()
                establish_jack_connections_reverb()
                # Donner les infos à l'ecran :
                send_tcp_info("info3_$Reverb :$$capture_1 -> playback_1&2$")
            elif arg == "pitch_high":
                launch_jalv_pitch_high()
                establish_jack_connections_pitch_high()
                # Donner les infos à l'ecran :
                send_tcp_info("info3_$Pitch High :$$capture_1 -> playback_1$")
            elif arg == "pitch_low":
                launch_jalv_pitch_low()
                establish_jack_connections_pitch_low()
                # Donner les infos à l'ecran :
                send_tcp_info("info3_$Pitch Low :$$capture_1 -> playback_1$")

            else:
                print(f"Instance '{arg}' non reconnue.")
    else:
        #Si aucune instance n'est spécifié, lancer le delay
        launch_jalv_delay()
        establish_jack_connections_delay()
        # Donner les infos à l'ecran :
        send_tcp_info("info3_$Delay 3s :$$capture_1 -> playback_1$")
elif variable == "stop":
    print("Arret de Jalv...")
    kill_all_jalv_instances()
    send_tcp_info("info3_$$           ...Not Running...$$")
else:
    print("La variable doit être 'start' ou 'start delay' ou 'start reverb' ou 'start pitch_high' ou 'start pitch_low' ou 'stop'")
    send_tcp_info("info3_$$           ...Not Running...$$")

