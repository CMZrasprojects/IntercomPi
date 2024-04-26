import RPi.GPIO as GPIO
import socket
import select
import subprocess

GPIO_PIN1 = 21
GPIO_PIN2 = 20
GPIO_PIN3 = 19
GPIO_PIN4 = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN1, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(GPIO_PIN2, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(GPIO_PIN3, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(GPIO_PIN4, GPIO.OUT, initial=GPIO.HIGH)
GPIO_STATE = GPIO.LOW

def switch_gpio1(state):
    GPIO.output(GPIO_PIN1, state)
def switch_gpio2(state):
    GPIO.output(GPIO_PIN2, state)
def switch_gpio3(state):
    GPIO.output(GPIO_PIN3, state)
def switch_gpio4(state):
    GPIO.output(GPIO_PIN4, state)

def handle_request(message):
    if message == "switch_1_on": #1
        switch_gpio1(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 1 :$$Switched On$")
    elif message == "switch_1_off":
        switch_gpio1(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 1 :$$Switched Off$")
    elif message == "switch_2_on": #2
        switch_gpio2(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 2 :$$Switched On$")
    elif message == "switch_2_off":
        switch_gpio2(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 2 :$$Switched Off$")
    elif message == "switch_3_on": #4
        switch_gpio3(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 3 :$$Switched On$")
    elif message == "switch_3_off":
        switch_gpio3(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 3 :$$Switched Off$")
    elif message == "switch_4_on": #8
        switch_gpio4(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 4 :$$Switched On$")
    elif message == "switch_4_off":
        switch_gpio4(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 4 :$$Switched Off$")

# Prog 8>3

    elif message == "switch_1&2_on": #3
        switch_gpio1(GPIO.LOW)
        switch_gpio2(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 1&2 :$$Switched On$")
    elif message == "switch_1&2_off":
        switch_gpio1(GPIO.HIGH)
        switch_gpio2(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 1&2 :$$Switched Off$")
    elif message == "switch_1&3_on": #5
        switch_gpio1(GPIO.LOW)
        switch_gpio3(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 1&3 :$$Switched On$")
    elif message == "switch_1&3_off":
        switch_gpio1(GPIO.HIGH)
        switch_gpio3(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 1&3 :$$Switched Off$")
    elif message == "switch_2&3_on": #6
        switch_gpio2(GPIO.LOW)
        switch_gpio3(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 2&3 :$$Switched On$")
    elif message == "switch_2&3_off":
        switch_gpio2(GPIO.HIGH)
        switch_gpio3(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 2&3 :$$Switched Off$")
    elif message == "switch_1&2&3_on": #7
        switch_gpio1(GPIO.LOW)
        switch_gpio2(GPIO.LOW)
        switch_gpio3(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 1&2&3 :$$Switched On$")
    elif message == "switch_1&2&3_off":
        switch_gpio1(GPIO.HIGH)
        switch_gpio2(GPIO.HIGH)
        switch_gpio3(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 1&2&3 :$$Switched Off$")

    elif message == "switch_1&4_on": #9
        switch_gpio1(GPIO.LOW)
        switch_gpio4(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 1&4 :$$Switched On$")
    elif message == "switch_1&4_off":
        switch_gpio1(GPIO.HIGH)
        switch_gpio4(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 1&4 :$$Switched Off$")
    elif message == "switch_2&4_on": #10
        switch_gpio2(GPIO.LOW)
        switch_gpio4(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 2&4 :$$Switched On$")
    elif message == "switch_2&4_off":
        switch_gpio2(GPIO.HIGH)
        switch_gpio4(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 2&4 :$$Switched Off$")
    elif message == "switch_1&2&4_on": #11
        switch_gpio1(GPIO.LOW)
        switch_gpio2(GPIO.LOW)
        switch_gpio4(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 1&2&4 :$$Switched On$")
    elif message == "switch_1&2&4_off":
        switch_gpio1(GPIO.HIGH)
        switch_gpio2(GPIO.HIGH)
        switch_gpio4(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 1&2&4 :$$Switched Off$")
    elif message == "switch_3&4_on": #12
        switch_gpio3(GPIO.LOW)
        switch_gpio4(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 3&4 :$$Switched On$")
    elif message == "switch_3&4_off":
        switch_gpio3(GPIO.HIGH)
        switch_gpio4(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 3&4 :$$Switched Off$")
    elif message == "switch_1&3&4_on": #13
        switch_gpio1(GPIO.LOW)
        switch_gpio3(GPIO.LOW)
        switch_gpio4(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 1&3&4 :$$Switched On$")
    elif message == "switch_1&3&4_off":
        switch_gpio1(GPIO.HIGH)
        switch_gpio3(GPIO.HIGH)
        switch_gpio4(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 1&3&4 :$$Switched Off$")
    elif message == "switch_2&3&4_on": #14
        switch_gpio2(GPIO.LOW)
        switch_gpio3(GPIO.LOW)
        switch_gpio4(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 2&3&4 :$$Switched On$")
    elif message == "switch_2&3&4_off":
        switch_gpio2(GPIO.HIGH)
        switch_gpio3(GPIO.HIGH)
        switch_gpio4(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 2&3&4 :$$Switched Off$")
    elif message == "switch_1&2&3&4_on": #15
        switch_gpio1(GPIO.LOW)
        switch_gpio2(GPIO.LOW)
        switch_gpio3(GPIO.LOW)
        switch_gpio4(GPIO.LOW)
        send_tcp_info("info2_$GPIO Out 1&2&3&4 :$$Switched On$")
    elif message == "switch_1&2&3&4_off":
        switch_gpio1(GPIO.HIGH)
        switch_gpio2(GPIO.HIGH)
        switch_gpio3(GPIO.HIGH)
        switch_gpio4(GPIO.HIGH)
        send_tcp_info("info2_$GPIO Out 1&2&3&4 :$$Switched Off$")
# Fin Prog 8>3

    elif message == "son1_on":
        subprocess.call(["aplay", "/home/pi/sons/son1.wav"])
    elif message == "son2_on":
        subprocess.call(["aplay", "/home/pi/sons/son2.wav"])
    elif message == "son3_on":
        subprocess.call(["aplay", "/home/pi/sons/son3.wav"])
    elif message == "son4_on":
        subprocess.call(["aplay", "/home/pi/sons/son4.wav"])
    elif message == "sons_off":
        subprocess.call(["pkill", "aplay"])

# Essai pour renvoyer des messages sur un autre port
def send_tcp_info(*args):
    try:
        # Assemblage de la chaîne de caractères
        data = ' '.join(map(str, args))

        # Créer un socket TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Se connecter au serveur distant (127.0.0.1:7002)
            s.connect(('127.0.0.1', 7002))
            # Envoi des données
            s.sendall(data.encode())
            print("Données envoyées :", data)
    except KeyboardInterrupt:
        raise KeyboardInterrupt  # Propage l'interruption au clavier
    except Exception as e:
        print("Une erreur s'est produite :", e)

# Configure TCP/UDP server
HOST = '127.0.0.1'  # Listen on all network interfaces
PORT = 8080  # Use the desired port number

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((HOST, PORT))
tcp_socket.listen(1)
print(f"Listening for TCP requests on port {PORT}...")
inputs = [tcp_socket]

while True:
    readable, _, _ = select.select(inputs, [], [])
    for sock in readable:
        if sock is tcp_socket:
            conn, addr = tcp_socket.accept()
            inputs.append(conn)
            print(f"Connected by {addr[0]}:{addr[1]}")
        else:
            conn = sock
            data = conn.recv(1024)
            if data:
                message = data.decode().strip()
                print(f"Received message: {message}")
                handle_request(message)
                response = "GPIO switched successfully\n"
                conn.sendall(response.encode())
                print(response)
            else:
                conn.close()
                inputs.remove(conn)

GPIO.cleanup()
