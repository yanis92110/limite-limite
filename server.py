import socket
import threading
clients = []
def creer_serveur():
        global clients
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", 5000))  # écoute sur le port 5000
        server.listen()

        print("Serveur en attente de connexions...")
        

        while True:
            conn, addr = server.accept()
            print("Connecté à", addr)
            clients.append((conn,addr))  # Ajoute le joueur à la liste
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
def get_clients_addr():
     return [addr for conn, addr in clients]

def handle_client(conn, addr):
    global clients
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            print(f"Reçu de {addr}:", data)
            conn.send(f"Echo: {data}".encode())  # renvoie un message
    finally:
        conn.close()
        clients = [c for c in clients if c[0] != conn]