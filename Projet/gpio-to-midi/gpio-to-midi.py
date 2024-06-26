import RPi.GPIO as GPIO
import time
import rtmidi
import socket
import os

# Configuration des broches GPIO pour les entrées
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

# Configuration RTP MIDI
#midi_out_physical = rtmidi.MidiOut()
midi_out_virtual = rtmidi.MidiOut()

# Ouvre le port MIDI physique
#midi_out_physical.open_port(0)  # Changez l'index de port si nécessaire
#print("Port RTP MIDI physique ouvert.")

# Ouvre le port MIDI virtuel
midi_out_virtual.open_virtual_port(b"GPIO-TO-MIDI")
print("Port MIDI virtuel ouvert.")

# Connecter le port MIDI "GPIO-TO-MIDI" au port VirMidi hw:0,0
os.system("aconnect 128:0 16:0")
print("Ports MIDI Connectés!")

# Tableau de correspondance entre les états des GPIO et les notes MIDI
gpio_to_note = {
    (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH): None,   # Rien
    (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH): 60,  # C4
    (GPIO.HIGH, GPIO.LOW, GPIO.HIGH, GPIO.HIGH): 62,  # D4
    (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH): 64,  # E4
    (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.HIGH): 65,  # F4
    (GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.HIGH): 67,  # G4
    (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH): 69,  # A4
    (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.HIGH): 71,  # B4
    (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.LOW): 72, # C5
    (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW): 74,   # D5
    (GPIO.HIGH, GPIO.LOW, GPIO.HIGH, GPIO.LOW): 76,   # E5
    (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.LOW): 77,   # F5
    (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW): 79,   # G5
    (GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.LOW): 81,   # A5
    (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.LOW): 83,   # B5
    (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW): 84,   # C6
}

# Fonction pour envoyer une note MIDI
def send_midi_note(midi_out, note, velocity):
    if note is not None:
        # Envoie la note MIDI "note on"
        midi_out.send_message([0x90, note, velocity])
        print("Note MIDI ON envoyée:", note)
    else:
        # Envoie la note MIDI "note off" avec vélocité 0
        midi_out.send_message([0x80, last_note, 0])
        print("Note MIDI OFF envoyée:", last_note)

# Fonction pour envoyer les infos au script ecran-oled pour affichage
def send_tcp_info(data):
    try:
        # Créer un socket TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Se connecter au serveur distant (127.0.0.1:7001)
            s.connect(('127.0.0.1', 7001))
            # Envoi des données
            s.sendall(data.encode())
            print("Données envoyées :", data)
    except KeyboardInterrupt:
        print("\nInterruption au clavier détectée. Arrêt du programme.")
    except Exception as e:
        print("Une erreur s'est produite :", e)

# Fonction pour attendre un certain temps et éviter les faux déclenchements
def debounce():
    time.sleep(0.05)  # Attend 50ms

# Fonction pour afficher
def send_tcp_info(*args):
    try:
        # Assemblage de la chaîne de caractères
        data = ' '.join(map(str, args))

        # Créer un socket TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Se connecter au serveur distant (127.0.0.1:7001)
            s.connect(('127.0.0.1', 7001))
            # Envoi des données
            s.sendall(data.encode())
            print("Données envoyées :", data)
    except Exception as e:
        print("Une erreur s'est produite :", e)

# Fonction pour décoder les changements de gpio
def decode_gpio_to_notes():
    last_state = (GPIO.input(22), GPIO.input(23), GPIO.input(24), GPIO.input(25))
    print("Démarrage de la surveillance des GPIO...")
    note_playing = False
    last_note = None
    try:
        while True:
            current_state = (GPIO.input(22), GPIO.input(23), GPIO.input(24), GPIO.input(25))
            if current_state != last_state:
                debounce()  # Attend avant de lire à nouveau l'état
                current_state = (GPIO.input(22), GPIO.input(23), GPIO.input(24), GPIO.input(25))
                print("Changement d'état détecté:", last_state, "->", current_state)
                last_state = current_state
                note = gpio_to_note.get(current_state)
                if note is not None:
                    if not note_playing:
                        #send_midi_note(midi_out_physical, note, 127)
                        send_midi_note(midi_out_virtual, note, 127)
                        send_tcp_info("info1_Changement d'etat :$", current_state, "$Note MIDI ON envoyee :$", note, "$")
                        note_playing = True
                        last_note = note
            elif note_playing and all(state == GPIO.HIGH for state in current_state):
                #send_midi_note(midi_out_physical, last_note, 0)
                send_midi_note(midi_out_virtual, last_note, 0)
                send_tcp_info("info1_Changement d'etat :$", current_state, "$Note MIDI OFF envoyee :$", last_note, "$")
                note_playing = False
            time.sleep(0.05)  # Attend 50ms avant la prochaine itération
    except KeyboardInterrupt:
        print("Interruption du programme par l'utilisateur.")
        GPIO.cleanup()

if __name__ == "__main__":
    decode_gpio_to_notes()
