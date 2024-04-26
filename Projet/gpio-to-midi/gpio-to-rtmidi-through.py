import RPi.GPIO as GPIO
import time
import rtmidi

# Configuration des broches GPIO pour les entrées
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

# Configuration RTP MIDI
midi_out = rtmidi.MidiOut()
available_ports = midi_out.get_ports()
selected_port = None

for port, name in enumerate(available_ports):
    if "14" in name:
        selected_port = port
        break

if selected_port is not None:
    midi_out.open_port(selected_port)
    print("Port MIDI ouvert:", available_ports[selected_port])
else:
    midi_out.open_virtual_port("RTP-MIDI")  # Ouvre un port virtuel si aucun port MIDI n'est disponible
    print("Aucun port MIDI physique disponible. Ouvre un port virtuel.")

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
    (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.LOW): 72,  # C5
}

# Fonction pour envoyer une note MIDI
def send_midi_note(note, velocity):
    if note is not None:
        # Envoie la note MIDI "note on"
        midi_out.send_message([0x90, note, velocity])
        print("Note MIDI ON envoyée:", note)
    else:
        # Envoie la note MIDI "note off" avec vélocité 0
        midi_out.send_message([0x80, last_note, 0])
        print("Note MIDI OFF envoyée:", last_note)

# Fonction pour attendre un certain temps et éviter les faux déclenchements
def debounce():
    time.sleep(0.05)  # Attend 50ms

def decode_gpio_to_notes():
    last_state = (GPIO.input(22), GPIO.input(23), GPIO.input(24), GPIO.input(25))
    print("Démarrage de la surveillance des GPIO...")
    note_playing = False
    last_note = None
    try:
        while True:
            current_state = (GPIO.input(22),GPIO.input(23), GPIO.input(24), GPIO.input(25))
            if current_state != last_state:
                debounce()  # Attend avant de lire à nouveau l'état
                current_state = (GPIO.input(22), GPIO.input(23), GPIO.input(24), GPIO.input(25))
                print("Changement d'état détecté:", last_state, "->", current_state)
                last_state = current_state
                note = gpio_to_note.get(current_state)
                if note is not None:
                    if not note_playing:
                        send_midi_note(note, 127)
                        note_playing = True
                        last_note = note
            elif note_playing and all(state == GPIO.HIGH for state in current_state):
                send_midi_note(last_note, 0)
                note_playing = False
    except KeyboardInterrupt:
        print("Interruption du programme par l'utilisateur.")
        GPIO.cleanup()

if __name__ == "__main__":
    decode_gpio_to_notes()
