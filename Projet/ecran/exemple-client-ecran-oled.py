import socket
import signal

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

# Gestion de l'interruption au clavier
def signal_handler(sig, frame):
    raise KeyboardInterrupt

# Installer le gestionnaire de signal
signal.signal(signal.SIGINT, signal_handler)

# Exemple d'utilisation de la fonction send_tcp_info
if __name__ == "__main__":
    print("Début du programme")
    try:
        while True:
            variable = etpuis
            # Appeler la fonction avec les données à envoyer
            send_tcp_info("info3_ça va commencer$", variable, "$ça va continuer$voila$cest fini")
    except KeyboardInterrupt:
        print("\nInterruption au clavier détectée. Arrêt du programme.")
