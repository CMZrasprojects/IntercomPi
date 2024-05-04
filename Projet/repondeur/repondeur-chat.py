import os
import time
import mido
import subprocess
import socket # Ecran
import signal # Ecran
import sys # Variable pour argument au lancement

#import pour Vosk :
import vosk
import wave
import json

#import pour gpt4free et google text to speech :
import g4f
from gtts import gTTS
from pydub import AudioSegment
import re

# Récupérer la variable passée en argument au lancement du script
if len(sys.argv) < 2:
    print("Usage: ./repondeur.py <variable>")
    sys.exit(1)

variable = sys.argv[1]


# Fonction pour afficher sur l'ecran
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
    except Exception as e:
        print("Une erreur s'est produite :", e)

# Fonction pour toujours pouvoir recuperer le filename du filepath selectionné :
def get_filename():
    # Supprimer le path '/home/pi/Projet/repondeur/recordings/' de la chaîne
    global filename_selected
    global selected_filepath
    selected_filepath = select_file()
    if selected_filepath:
        filename_selected = selected_filepath.replace('/home/pi/Projet/repondeur/recordings/', '')
        print("filename_selected :", filename_selected)
    else:
        print("plus aucun fichier")
        send_tcp_info("info4_$Plus aucun fichier$selectionné...$$")

# Fonction pour envoyer des notes Midi
def send_midi_message(note, is_note_on, velocity, port_name="Midi Through Port-0"):
    try:
        msg_type = 'note_on' if is_note_on else 'note_off'
        msg = mido.Message(msg_type, note=note, velocity=velocity)
        with mido.open_output(port_name) as port:
            port.send(msg)
    except Exception as e:
        print("Error:", e)

# Fonction pour recevoir des notes Midi
def receive_midi_messages(port_name="Midi Through Port-0"):
    try:
        with mido.open_input(port_name) as port:
            print(f"Listening for MIDI messages on port '{port_name}'...")
            for msg in port:
                yield msg
    except Exception as e:
        print("Error:", e)

# Variables globales pour être affichées n'importe où
global filename, filepath, filename_selected

# Fonction pour enregistrer un fichier audio
def start_recording():
#    send_tcp_info("info4_$Recording Message ...$$", filename, "$")
    current_time = time.strftime("%H-%M-%S_%d-%m-%y")
    filename = f"RecRep_{current_time}.wav"
    filepath = f"/home/pi/Projet/repondeur/recordings/{filename}"
    send_tcp_info("info4_$Recording Message ...$$", filename, "$")
    subprocess.Popen(["jack_capture", "-c", "1", "-p", "system:capture_1", filepath])
    file_number = get_next_file_number()  # Obtenir le numéro de fichier
    update_log(file_number, filepath, True, True)  # Nouveau fichier enregistré, non lu, selectionné
    update_log_last_selected() # Deselectionner le precedent
    return filename, filepath  # Retourne le nom de fichier et le chemin complet

# Fonction pour enregistrer l'annonce d'accueil
def start_recording_accueil():
    subprocess.Popen(["jack_capture", "-c", "1", "-p", "system:capture_1", "/home/pi/Projet/repondeur/recordings/accueil/accueil.wav"])

# Fonction pour arrêter l'enregistrement
def stop_recording():
    subprocess.Popen(["killall", "jack_capture"])

# Fonction pour lire un fichier audio
def play_audio(filepath):
    subprocess.Popen(["/home/pi/EnvPython/bin/python3", "/home/pi/Projet/repondeur/play_file.py", filepath])
    get_filename()
    send_tcp_info("info4_$Playing selected message :$$", filename_selected, "$")

# Fonction pour arreter la lecture
def stop_audio():

    # Utiliser la commande kill pour arrêter le processus de lecture audio
    subprocess.run(["pkill", "-f", "play_file.py"])

# Fonction pour lire l'annonce d'accueil :
def play_audio_accueil():
    subprocess.Popen(["/home/pi/EnvPython/bin/python3", "/home/pi/Projet/repondeur/play_file.py", "/home/pi/Projet/repondeur/recordings/accueil/accueil.wav"])

# Fonction pour lire une musique d'attente :
def play_audio_attente():
    subprocess.Popen(["/home/pi/EnvPython/bin/python3", "/home/pi/Projet/repondeur/play_file.py", "/home/pi/Projet/repondeur/recordings/accueil/attente.wav"])

# Fonction pour supprimer un fichier audio
def delete_audio(filepath):
    os.remove(filepath)

# Fonction pour mettre à jour le fichier de log à appeler à la création d'un nouveau enregistrement
def update_log(file_number, filepath, has_message, selected_file):
    # Lecture du fichier log
    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "r") as log_file:
        lines = log_file.readlines()

    # Mise à jour du fichier log avec les nouvelles informations
    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "w") as log_file:
        # Réécrit les lignes existantes
        log_file.writelines(lines)

        # Ajout du nouveau fichier enregistré et sélectionné
        log_file.write(f"{file_number} {filepath} {str(has_message)} {str(selected_file)}\n")

# Fonction pour mettre à jour le log en passant has_message à False ("Vous n'avez pas de nouveau message !")
def update_log_played(filepath, has_message):
    # Lecture du fichier log
    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "r") as log_file:
        lines = log_file.readlines()

    # Recherche de la ligne correspondante et mise à jour du fichier log
    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "w") as log_file:
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1] == filepath:
                # Mise à jour de la troisième partie de la ligne à False
                log_file.write(f"{parts[0]} {parts[1]} {str(has_message)} {parts[3]}\n")
            else:
                log_file.write(line)


# Fonction pour mettre à jour la derniere ligne (dernier enregistrement) comme "selected" 
# A mettre à chaque enregistrement, et note pour selectionner le dernier (combiner avec select_file())
def update_log_last_selected():
    try:
        # Lecture du fichier journal
        with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "r") as log_file:
            lines = log_file.readlines()

        # Mise à jour du fichier journal avec les nouvelles informations
        with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "w") as log_file:
            for index, line in enumerate(lines):
                parts = line.strip().split()
                if index == len(lines) - 1:
                    # La dernière ligne est sélectionnée
                    log_file.write(f"{parts[0]} {parts[1]} {parts[2]} True\n")
                else:
                    # Toutes les autres lignes ne sont pas sélectionnées
                    log_file.write(f"{parts[0]} {parts[1]} {parts[2]} False\n")
    except FileNotFoundError:
        print("Le fichier de journal n'a pas été trouvé.")

# Fonction pour mettre à jour le fichier selectionné vers le haut (plus ancien)
def update_log_next_selected():
    # Lecture du fichier log
    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "r") as log_file:
        lines = log_file.readlines()#

    # Recherche de la ligne où la 4eme partie est True
    for i, line in enumerate(lines):
        parts = line.strip().split()
        if len(parts) >= 4 and parts[3] == "True":
            # Mise à jour de la valeur en True pour la quatrième partie de la ligne précédente
            if i > 0:
                prev_parts = lines[i - 1].strip().split()
                if len(prev_parts) >= 4:
                    prev_parts[3] = "True"
                    lines[i - 1] = " ".join(prev_parts) + "\n"
            else:
                break
            # Passer la quatrième partie de la ligne actuelle à False
            parts[3] = "False"
            lines[i] = " ".join(parts) + "\n"
            break#

    # Réécriture du fichier de log
    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "w") as log_file:
        for line in lines:
            log_file.write(line)

# Fonction pour mettre à jour le fichier selectionné vers le bas (plus récent)
def update_log_prev_selected():
    # Lecture du fichier log
    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "r") as log_file:
        lines = log_file.readlines()

    # Recherche de la ligne où la 4eme partie est True
    for i, line in enumerate(lines):
        parts = line.strip().split()
        if len(parts) >= 4 and parts[3] == "True":
            # Mise à jour de la valeur en True pour la quatrième partie de la ligne suivante
            if i < len(lines) - 1:
                next_parts = lines[i + 1].strip().split()
                if len(next_parts) >= 4:
                    next_parts[3] = "True"
                    lines[i + 1] = " ".join(next_parts) + "\n"
            else:
                break

            # Passer la quatrième partie de la ligne actuelle à False
            parts[3] = "False"
            lines[i] = " ".join(parts) + "\n"
            break

    # Réécriture du fichier de log
    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "w") as log_file:
        for line in lines:
            log_file.write(line)

# Fonction pour sélectionner le fichier "selected"
def select_file():
    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "r") as log_file:
        lines = log_file.readlines()

    selected_file = None
    for i, line in enumerate(lines):
        print(f"Ligne {i+1} :", repr(line))
    for line in lines:
        parts = line.strip().split()
        print("parts :", parts)
        if len(parts) >= 1 and parts[3] == "True":
            selected_file = parts[1]
            print("fichier selectionne :", selected_file)
            break
    return selected_file
    print ("selected_file :", selected_file)
# Fonction pour obtenir le numéro du prochain fichier OK
def get_next_file_number():

    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "r") as log_file:
        lines = log_file.readlines()
    if lines:
        last_line = lines[-1]
        parts = last_line.strip().split()
        if parts:
            print("Nombre de lignes dans le fichier de log :", len(lines))
            return int(parts[0]) + 1
            print("Prochain numéro", int(parts[0]) + 1)
        print("Aucune ligne dans le fichier de log. Retourner 1 pour le premier numéro d'ID.")
    return 1

# Supprimer la ligne selected dans le log et le fichier correspondant sur le disque
def delete_selected(selected_file):
    # Suppression du fichier audio
    if os.path.exists(selected_file):
        os.remove(selected_file)

    # Lecture du fichier log
    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "r") as log_file:
        lines = log_file.readlines()
        print("lines :", lines)
    # Construction d'une nouvelle liste de lignes sans la ligne à supprimer
    new_lines = []
    for line in lines:
        parts = line.strip().split()
        print("parts :", parts)
        if len(parts) >= 1 and parts[1] != selected_file:  # Vérification si la deuxième partie correspond à >
            new_lines.append(line)
            print("new_lines :", new_lines)
    # Réécriture du fichier de log
    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "w") as log_file:
        for line in new_lines:
            log_file.write(line)
            print("ecriture de line :", line)

# Supprimer tous les fichiers et lignes du log, sauf le dernier enregistrement
def delete_all_but_last():
    # Lecture du fichier log
    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "r") as log_file:
        lines = log_file.readlines()

    # Suppression des fichiers et des lignes du log
    for line in lines[:-1]:  # Tout sauf la dernière ligne
        parts = line.strip().split()
        if len(parts) >= 2:
            filepath = parts[1]
            # Suppression du fichier sauf si c'est le fichier log
            if os.path.exists(filepath) and not filepath.endswith("log-recordings.txt"):
                os.remove(filepath)

    # Réécriture du fichier de log avec la dernière ligne
    with open("/home/pi/Projet/repondeur/recordings/log-recordings.txt", "w") as log_file:
        if lines:  # S'il y a des lignes dans le fichier de log
            last_line = lines[-1].strip()  # Récupération de la dernière ligne
            log_file.write(last_line + "\n")  # Réécriture de la dernière ligne

# Transcrire un enregistrement audio en fichier texte dans le dossier "transcription"
def transcrire_audio(path_audio_a_transcrire):
    # Chemin vers le modèle Vosk pré-entraîné pour le français
    MODEL_PATH = "/home/pi/libVosk/vosk-model-small-fr-0.22"

    # Fonction pour convertir le fichier audio au format PCM 16 kHz 16 bits mono
    def convert_audio(input_file, output_file):
        subprocess.run(["ffmpeg", "-i", input_file, "-ar", "16000", "-ac", "1", "-sample_fmt", "s16", output_file])

    # Fonction pour écrire le résultat dans un fichier texte
    def ecrire_resultat(texte_transcrit, path_audio):
        # Extraire le nom du fichier audio sans l'extension
        nom_fichier_audio = os.path.basename(path_audio)
        nom_fichier_sans_extension = os.path.splitext(nom_fichier_audio)[0]

        # Chemin complet du fichier texte de sortie
        path_fichier_texte = os.path.join("/home/pi/Projet/repondeur/transcription", nom_fichier_sans_extension + ".txt")

        # Écrire le texte transcrit dans le fichier texte de sortie
        with open(path_fichier_texte, "w") as fichier_texte:
            fichier_texte.write(texte_transcrit)

    # Convertir le fichier audio si nécessaire et obtenir son nom converti
    converted_audio_file = path_audio_a_transcrire.replace(".wav", "_converted.wav")
    convert_audio(path_audio_a_transcrire, converted_audio_file)

    # Initialiser le modèle Vosk avec le modèle français
    model = vosk.Model(MODEL_PATH)

    # Ouvrir le fichier audio converti
    with wave.open(converted_audio_file, "rb") as wf:
        # Créer un objet Recognizer
        recognizer = vosk.KaldiRecognizer(model, wf.getframerate())

        texte_transcrit = ""

        # Lecture des données audio par blocs
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                # Récupérer le résultat de la transcription
                result = json.loads(recognizer.Result())
                texte_transcrit += result["text"] + "\n"

        # Récupérer le résultat final de la transcription
        result = json.loads(recognizer.FinalResult())
        texte_transcrit += result["text"] + "\n"

    # Supprimer le fichier audio converti après la transcription
    os.remove(converted_audio_file)

    # Écrire le résultat dans un fichier texte
    ecrire_resultat(texte_transcrit, path_audio_a_transcrire)

    return texte_transcrit

## Exemple d'utilisation de la fonction
#path_audio_a_transcrire = "/home/pi/Projet/repondeur/recordings/accueil/accueil.wav"
#texte_transcrit = transcrire_audio(path_audio_a_transcrire)
#print(texte_transcrit)

# Enregistrer une question pour le chat
def record_audio_chat():
    send_tcp_info("info4_$Enregistrement d'une Question...$$$")
    subprocess.Popen(["jack_capture", "-c", "1", "-p", "system:capture_1", "/home/pi/Projet/repondeur/chat/question.wav"])

# Fonction pour transcrire la question pour le chat
def transcrire_audio_chat(path_audio_a_transcrire):
    # Chemin vers le modèle Vosk pré-entraîné pour le français
    MODEL_PATH = "/home/pi/libVosk/vosk-model-small-fr-0.22"

    # Fonction pour convertir le fichier audio au format PCM 16 kHz 16 bits mono
    def convert_audio(input_file, output_file):
        subprocess.run(["ffmpeg", "-i", input_file, "-ar", "16000", "-ac", "1", "-sample_fmt", "s16", output_file])

    # Fonction pour écrire le résultat dans un fichier texte
    def ecrire_resultat(texte_transcrit, path_audio):
        # Extraire le nom du fichier audio sans l'extension
        nom_fichier_audio = os.path.basename(path_audio)
        nom_fichier_sans_extension = os.path.splitext(nom_fichier_audio)[0]

        # Chemin complet du fichier texte de sortie
        path_fichier_texte = os.path.join("/home/pi/Projet/repondeur/chat", "question.txt")

        # Écrire le texte transcrit dans le fichier texte de sortie
        with open(path_fichier_texte, "w") as fichier_texte:
            fichier_texte.write(texte_transcrit)

    # Convertir le fichier audio si nécessaire et obtenir son nom converti
    converted_audio_file = path_audio_a_transcrire.replace(".wav", "_converted.wav")
    convert_audio(path_audio_a_transcrire, converted_audio_file)

    # Initialiser le modèle Vosk avec le modèle français
    model = vosk.Model(MODEL_PATH)

    # Ouvrir le fichier audio converti
    with wave.open(converted_audio_file, "rb") as wf:
        # Créer un objet Recognizer
        recognizer = vosk.KaldiRecognizer(model, wf.getframerate())

        question_transcrit = ""

        # Lecture des données audio par blocs
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                # Récupérer le résultat de la transcription
                result = json.loads(recognizer.Result())
                question_transcrit += result["text"] + "\n"

        # Récupérer le résultat final de la transcription
        result = json.loads(recognizer.FinalResult())
        question_transcrit += result["text"] + "\n"

    # Supprimer le fichier audio converti après la transcription
    os.remove(converted_audio_file)

    # Écrire le résultat dans un fichier texte
    ecrire_resultat(question_transcrit, path_audio_a_transcrire)
    print(question_transcrit)
    send_tcp_info("info4_$Question :$$", question_transcrit, "$")
    return question_transcrit

# Fonction pour envoyer la question, recevoir la reponse, l'ecrire dans un fichier, et lire la reponse :
def play_audio_chat(question_chat):
    g4f.debug.logging = False  # Enable debug logging
    g4f.debug.version_check = False  # Disable automatic version checking
    print(g4f.Provider.Bing.params)
    send_tcp_info("info4_$Generation de la réponse...$$$")
    ## Normal response
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4,
        messages=[{"role": "user", "content": question_chat}],
    )

    # Récupérer la réponse transcrite
    reponse_transcrit = response

    # Supprimer les caractères spéciaux et les emojis du texte
    reponse_propre = re.sub(r'[^\w\s.!?]', '', reponse_transcrit)

    # Créer un objet gTTS avec le texte transcrit
    tts = gTTS(text=reponse_propre, lang="fr")

    # Enregistrer la réponse transcrite dans un fichier audio
    fichier_mp3 = "/home/pi/Projet/repondeur/chat/reponse.mp3"
    tts.save(fichier_mp3)

    # Rééchantillonner le fichier MP3 à 48 kHz et le convertir en WAV
    audio = AudioSegment.from_mp3(fichier_mp3).set_frame_rate(48000)
    fichier_wav = fichier_mp3[:-4] + ".wav"  # Renommer en .wav
    audio.export(fichier_wav, format="wav")


    # Jouer le fichier audio
    subprocess.Popen(["/home/pi/EnvPython/bin/python3", "/home/pi/Projet/repondeur/play_file.py", fichier_wav])

    # Afficher la réponse transcrite
    print(reponse_propre)
    send_tcp_info("info4_$Reponse :$$", reponse_propre, "$")


# Pour debug
def rien():
    time.sleep(0.1)

# Lancement de la boucle
if variable == "start":

# Boucle principale
    for msg in receive_midi_messages():  # Recevoir les messages MIDI
        note = msg.note
        is_note_on = True if msg.type == 'note_on' else False
        velocity = msg.velocity

        if note == 60:  # Note C4 : Enregistrer un nouveau message
            if is_note_on:
                if velocity == 127:
                    play_audio_accueil()
                    last_recorded_filename, last_recorded_filepath = start_recording()
                elif velocity == 0:
                    stop_recording()
                    send_tcp_info("info4_$Fin de l'enregistrement$$T'as au moins un message !$")
        elif note == 62:  # Note D4 : Lire le fichier selectionné
            if is_note_on:
                if velocity == 0:
                    stop_audio()
                elif velocity == 127:
                    selected_file = select_file()
                    if selected_file:
                        play_audio(selected_file)
                        update_log_played(filepath = selected_file, has_message=False)
        elif note == 64:  # Note E4 : Selectionner fichier en haut de la liste (le plus récent)
            if is_note_on and velocity == 127:
                update_log_last_selected()
                get_filename()
                send_tcp_info("info4_$Dernier message selectionné$$", filename_selected, "$")
        elif note == 65:  # Note F4 :Transcrire le fichier audio selectionné en texte, poser la question à bing-gpt puis lire la reponse avec gtts
            if is_note_on:
                if velocity == 127:
                    send_tcp_info("info4_$Chat en cours...$$$")
                    record_audio_chat()
                elif velocity == 0:
                    stop_recording()
                    question_transcrit = transcrire_audio_chat("/home/pi/Projet/repondeur/chat/question.wav")
                    play_audio_chat(question_transcrit)
        elif note == 67:  # Note G4 : Lire une musique d'attente
            if is_note_on and velocity == 127:
                play_audio_attente()
                send_tcp_info("info4_$Musique d'attente$$en lecture...$")
        elif note == 69:  # Note A4 : Supprimer le fichier selectionné et selectionner le plus récent
            if is_note_on and velocity == 127:
                selected_file = select_file()
                delete_selected(selected_file)
                get_filename()
                send_tcp_info("info4_$Suppression du message$selectionné :$", filename_selected, "$")
                time.sleep(0.1)
                update_log_last_selected()
        elif note == 71:  # Note B4 : Arreter la lecture audio
            if is_note_on and velocity == 127:
                stop_audio()
                send_tcp_info("info4_$Arret de la lecture$$$")
        elif note == 72:  # Note C5 : Selectionner fichier suivant (plus ancien)
            if is_note_on and velocity == 127:
                update_log_next_selected()
                get_filename()
                send_tcp_info("info4_$Message selectionné :$$", filename_selected, "$")
        elif note == 74:  # Note D5 : Selectionner fichier précédent (plus récent)
            if is_note_on and velocity == 127:
                update_log_prev_selected()
                get_filename()
                send_tcp_info("info4_$Message selectionné :$$", filename_selected, "$")
        elif note == 76:  # Note E5 : Supprimer tous les fichiers sauf le dernier
            if is_note_on and velocity == 127:
                delete_all_but_last()
                send_tcp_info("info4_$Suppression de tous$$les messages$")
                update_log_last_selected()
        elif note == 77:  # Note F5 : Enregistrer Annonce d'accueil
            if is_note_on:
                if velocity == 127:
                    start_recording_accueil()
                    send_tcp_info("info4_$Enregistrement d'un$nouveau message$d'accueil$Soit bon !")
                elif velocity == 0:
                    stop_recording()
        elif note == 79:  # Note G5 : Transcrire le fichier selectionné en texte dans le dossier transcription
            if is_note_on and velocity == 127:
                selected_file = select_file()
                path_audio_a_transcrire = selected_file
                texte_transcrit = transcrire_audio(path_audio_a_transcrire)
                send_tcp_info("info4_$Transcription...$$$")

        time.sleep(0.1)  # Attendre un court instant avant de vérifier à nouveau les messages MIDI

elif variable == "stop":
    # Ajoutez ici le code pour arrêter votre fonction
    print("Arrêt de la fonction...")
    send_tcp_info("info4_$$           ...ARRET...$$")
    subprocess.run(["pkill", "-f", "/home/pi/EnvPython/bin/python /home/pi/Projet/repondeur/repondeur.py start"]) # Quitter le script
else:
    print("Usage: ./repondeur.py start|stop")
