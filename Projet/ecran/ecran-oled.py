import RPi.GPIO as GPIO
import time
import netifaces as ni
import socket
import threading
import subprocess
import psutil

#Gestion de l'ecran :

import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import time

# Définition des constantes pour la largeur et la hauteur de l'écran OLED
WIDTH = 128
HEIGHT = 64

# Initialisation du bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Initialisation de l'écran OLED
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Charge la police par défaut
font = ImageFont.load_default()

def show_oled(line1, *args):

    if len(args) == 1:
        line2, line3, line4, line5, line6 = args[0]
    else:
        line2, line3, line4, line5, line6 = args

    # Efface l'écran
    oled.fill(0)
    oled.show()

    # Crée une image vide avec un fond noir
    image = Image.new('1', (WIDTH, HEIGHT))

    # Crée un objet dessin pour l'image
    draw = ImageDraw.Draw(image)

    # Dessine les lignes de texte sur l'écran
    draw.text((0, 0), line1, font=font, fill=255)
    draw.text((4, 12), line2, font=font, fill=255)
    draw.text((4, 22), line3, font=font, fill=255)
    draw.text((4, 32), line4, font=font, fill=255)
    draw.text((4, 42), line5, font=font, fill=255)
    draw.text((4, 52), line6, font=font, fill=255)

    # Affiche l'image sur l'écran
    oled.image(image)
    oled.show()

# Exemple d'utilisation de la fonction
# show_oled('Bonjour!', 'Ceci est un exemple', "d'écran OLED!", 'C'est', 'Génial', '!!!')
# show_oled('Bonjour!', ('Ceci est un exemple', "d'écran OLED!", 'C'est', 'Génial', '!!!'))
# show_oled('Bonjour! Infos du jour :', variable_tuple_x5)
#
# Nettoyer l'écran et quitter
# oled.fill(0)
# oled.show()

# Configuration des broches GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Activation de la résistance de pull-u ou downp

# Fonction pour obtenir l'adresse IP d'une interface
def get_ip(interface):
    try:
        ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
    except KeyError:
        ip = "N/A"
    return ip

# Fonction pour obtenir le SSID du wifi connecté
def get_wifi_ssid():
    try:
        result = subprocess.run(['iwgetid', '--raw'], capture_output=True, text=True)
        ssid = result.stdout.strip()
        return ssid
    except FileNotFoundError:
        return 'SSID inconnu'

# Exemple d'utilisation
ssid = get_wifi_ssid()

# Variables globales pour stocker les adresses IP précédentes
previous_eth0_ip = None
previous_wlan0_ip = None

# Fonction pour afficher les adresses IP
def print_ip_addresses():
    global previous_eth0_ip, previous_wlan0_ip
    eth0_ip = get_ip('eth0')
    wlan0_ip = get_ip('wlan0')

    # Vérifier si les adresses IP ont changé avant de les afficher
    if eth0_ip != previous_eth0_ip or wlan0_ip != previous_wlan0_ip:
        print(f"eth0 IP: {eth0_ip}, wlan0 IP: {wlan0_ip}")
        show_oled("Interface eth0 IP:", str(eth0_ip), "Interface Wifi wlan0 IP:", get_wifi_ssid(), str(wlan0_ip), '')

        # Mettre à jour les adresses IP précédentes
        previous_eth0_ip = eth0_ip
        previous_wlan0_ip = wlan0_ip

# Fonction pour recevoir les données TCP sur le port spécifié
def receive_tcp_data(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permet la réutilisation de l'adresse
            s.bind(('127.0.0.1', port))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024).decode('utf-8')
                    if data:
                        yield data
    except Exception as e:
        print(f"Error receiving TCP data on port {port}: {e}")

# Fonction pour filtrer les données en fonction de l'en-tête
def filter_data(data, expected_header):
    if data.startswith(expected_header):
        return data[len(expected_header):]
    return None

# Fonction pour transformer les données filtrées reçues en tuple

def transform_data(filtered_data):
    # Séparation des données en utilisant le signe '$'
    parts = filtered_data.split('$')

    # Vérification s'il y a exactement 5 parties
    if len(parts) == 5:
        # Création du tuple avec les 5 parties
        new_tuple = tuple(parts)
        return new_tuple
    else:
        print("Erreur: Les données ne sont pas au bon format.")
        return None

# Variables pour affichage constant
wait_next = False

# Variables pour les paramètres de filtre
filter_header = "info1_"
script_header = "Scripte_1 Infos :"

# Fonction pour le state 0
def state_0():
    print("State 0: Getting IP addresses...")
   # get_ip()
    print_ip_addresses()

# Fonction pour les state intermediaires (1, 3, 4)
#def state_6():
#    filter_header = "info1_"
#    script_header = "Scripte_1 Infos :"
#    print("Page Info State 1")
#    show_oled(script_header, 'State 1:', 'Filter header set to :', 'info1_', '', '')
#    current_state = 2

# Fonction pour le state 2
def state_2():
    global filter_header, script_header
    filter_header = "info1_"
    script_header = "GPIO-to-MIDI Infos :"
    print("State 1: Filter header set to 'info1_'")

# Fonction pour le state 4
def state_4():
    global filter_header, script_header
    filter_header = "info2_"
    script_header = "TCP-to-GPIO Infos :"
    print("State 2: Filter header set to 'info2_'")

# Fonction pour le state 6
def state_6():
    global filter_header, script_header
    filter_header = "info3_"
    script_header = "Delay-3s Infos :"
    print("State 3: Filter header set to 'info3_'")

# Fonction pour le state 8
def state_8():
    global filter_header, script_header
    filter_header = "info4_"
    script_header = "Repondeur Infos :"
    print("State 3: Filter header set to 'info3_'")

# Fonction pour le state 10
def state_10():
    global filter_header, script_header
    filter_header = "info5_"
    script_header = "Companion Infos :"
    print("State 3: Filter header set to 'info3_'")

# Fonction pour exécuter receive_tcp_data en arrière-plan sur le port 7001
def receive1_tcp_data_background():
    for data in receive_tcp_data(7001):
        filtered_data = filter_data(data, filter_header)
        if filtered_data:
            print("Données filtrées :", filtered_data)
            # Transformation des données filtrées en tuple à 5 arguments
            new_tuple = transform_data(filtered_data)
            if new_tuple:
                print("Données filtrées en tuple :", new_tuple)
            show_oled(script_header, new_tuple)

# Fonction pour exécuter receive_tcp_data en arrière-plan sur le port 7002
def receive2_tcp_data_background():
    for data in receive_tcp_data(7002):
        filtered_data = filter_data(data, filter_header)
        if filtered_data:
            print("Données filtrées :", filtered_data)
            # Transformation des données filtrées en tuple à 5 arguments
            new_tuple = transform_data(filtered_data)
            if new_tuple:
                print("Données filtrées en tuple :", new_tuple)
            show_oled(script_header, new_tuple)

# Fonction pour exécuter receive_tcp_data en arrière-plan sur le port 7003
def receive3_tcp_data_background():
    for data in receive_tcp_data(7003):
        filtered_data = filter_data(data, filter_header)
        if filtered_data:
            print("Données filtrées :", filtered_data)
            # Transformation des données filtrées en tuple à 5 arguments
            new_tuple = transform_data(filtered_data)
            if new_tuple:
                print("Données filtrées en tuple :", new_tuple)
            show_oled(script_header, new_tuple)

# Fonction pour exécuter receive_tcp_data en arrière-plan sur le port 7004
def receive4_tcp_data_background():
    for data in receive_tcp_data(7004):
        filtered_data = filter_data(data, filter_header)
        if filtered_data:
            print("Données filtrées :", filtered_data)
            # Transformation des données filtrées en tuple à 5 arguments
            new_tuple = transform_data(filtered_data)
            if new_tuple:
                print("Données filtrées en tuple :", new_tuple)
            show_oled(script_header, new_tuple)

# Fonction pour exécuter receive_tcp_data en arrière-plan sur le port 7005
def receive5_tcp_data_background():
    for data in receive_tcp_data(7005):
        filtered_data = filter_data(data, filter_header)
        if filtered_data:
            print("Données filtrées :", filtered_data)
            # Transformation des données filtrées en tuple à 5 arguments
            new_tuple = transform_data(filtered_data)
            if new_tuple:
                print("Données filtrées en tuple :", new_tuple)
            show_oled(script_header, new_tuple)

# Fonction pour vérifier si un processus est executé
def check_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

# Fonction pour vérifier si un service est actif
def check_service_running(service_name):
    try:
        subprocess.run(["systemctl", "is-active", "--quiet", service_name], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# Match-case pour déterminer l'état et exécuter la fonction correspondante
def main():
    current_state = 13
    prev_input = GPIO.input(17)


    # Démarrer le thread pour recevoir les données TCP en arrière-plan
    receive1_thread = threading.Thread(target=receive1_tcp_data_background)
    receive2_thread = threading.Thread(target=receive2_tcp_data_background)
    receive3_thread = threading.Thread(target=receive3_tcp_data_background)
    receive4_thread = threading.Thread(target=receive4_tcp_data_background)
    receive5_thread = threading.Thread(target=receive5_tcp_data_background)
    receive1_thread.daemon = True  # Le thread s'arrêtera lorsque le programme principal s'arrête
    receive2_thread.daemon = True  # Le thread s'arrêtera lorsque le programme principal s'arrête
    receive3_thread.daemon = True  # Le thread s'arrêtera lorsque le programme principal s'arrête
    receive4_thread.daemon = True  # Le thread s'arrêtera lorsque le programme principal s'arrête
    receive5_thread.daemon = True  # Le thread s'arrêtera lorsque le programme principal s'arrête
    receive1_thread.start()
    receive2_thread.start()
    receive3_thread.start()
    receive4_thread.start()
    receive5_thread.start()
    try:
        while True:
             input_state = GPIO.input(17)
             if input_state == GPIO.LOW and prev_input == GPIO.HIGH:
                 current_state = (current_state + 1) % 14
             prev_input = input_state

             match current_state:
                 case 0:
                     state_0()
                 case 1:
                     filter_header = "info1_"
                     script_header = "GPIO-to-MIDI Infos :"
                     print("Page Info State 1")
                     show_oled(script_header, ('TCP Port 7001', 'Filter header set to :', 'info1_', '', ''))
                     time.sleep(1)
                     if check_service_running("gpio-to-midi"):
                         show_oled(script_header, ('', 'Service Status :', '', 'Running', ''))
                     else:
                         show_oled(script_header, ('', 'Service Status :', '', 'Not Running', ''))
                     current_state = 2
                 case 2:
                     state_2()
                 case 3:
                     filter_header = "info2_"
                     script_header = "TCP-to-GPIO Infos :"
                     print("Page Info State 3")
                     show_oled(script_header, 'TCP Port 7002', 'Filter header set to :', 'info2_', '', '')
                     time.sleep(1)
                     if check_service_running("tcp-to-gpio"):
                         show_oled(script_header, ('', 'Service Status :', '', 'Running', ''))
                     else:
                         show_oled(script_header, ('', 'Service Status :', '', 'Not Running', ''))
                     current_state = 4
                 case 4:
                     state_4()
                 case 5:
                     filter_header = "info3_"
                     script_header = "Delay-3s Infos :"
                     print("Page Info State 5")
                     show_oled(script_header, 'TCP Port 7003', 'Filter header set to :', 'info3_', '', '')
                     time.sleep(1)
                     if check_process_running("jalv"):
                         show_oled(script_header, ('', 'Processus Status :', '', 'Running', ''))
                     else:
                         show_oled(script_header, ('', 'Processus Status :', '', 'Not Running', ''))
                     current_state = 6
                 case 6:
                     state_6()
                 case 7:
                     filter_header = "info4_"
                     script_header = "Repondeur Infos :"
                     print("Page Info State 7")
                     show_oled(script_header, 'TCP Port 7004', 'Filter header set to :', 'info4_', '', '')
                     time.sleep(1)
                     if check_process_running("EnvPython/bin/python /home/pi/Projet/repondeur/repondeur.py start"):
                         show_oled(script_header, ('', 'Processus Status :', '', 'Running', ''))
                     else:
                         show_oled(script_header, ('', 'Processus Status :', '', 'Not Running', ''))

                     current_state = 8
                 case 8:
                     state_8()
                 case 9:
                     filter_header = "info5_"
                     script_header = "Companion Infos :"
                     print("Page Info State 9")
                     time.sleep(1)
                     if check_service_running("companion"):
                         show_oled(script_header, ('', 'Service Status :', '', 'Running', ''))
                     else:
                         show_oled(script_header, ('', 'Service Status :', '', 'Not Running', ''))
                     show_oled(script_header, 'TCP Port 7005', 'Filter header set to :', 'info5_', '', '')
                     current_state = 10
                 case 10:
                     state_10()
                 case 11:
                     global previous_eth0_ip, previous_wlan0_ip
                     previous_eth0_ip = None
                     previous_wlan0_ip = None
                     show_oled('', '', '              -- STANDBY --', '', '', '')
                     time.sleep(1)
                     current_state = 12
                 case 12:
                     oled.fill(0)
                     oled.show()
                     current_state = 13
                 case 13:
                     print("Standby")
             time.sleep(0.1)

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Cleaning up GPIO and OLED...")
    finally:
        GPIO.cleanup()
        # Efface l'écran
        oled.fill(0)
        oled.show()
# Démarrer le programme
if __name__ == "__main__":
    main()
