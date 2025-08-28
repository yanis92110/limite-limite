import socket
import threading
import json
from Jeu import Jeu


clients = []
jeu_instance = None
pseudos = {}  # Dictionnaire pour associer les sockets aux pseudos

def creer_serveur():
    global clients, jeu_instance
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5000))
    server.listen()
    
    print("Serveur en attente de connexions...")
    # Permettre à l'hébergeur de rejoindre son propre serveur en tant que client
    def rejoindre_en_tant_que_client(pseudo="Hebergeur"):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 5000))
        clients.append(client)
        pseudos[client] = pseudo
        threading.Thread(target=handle_client, args=(client, ("127.0.0.1", 5000)), daemon=True).start()

    # Appeler la fonction pour que l'hébergeur rejoigne automatiquement
    #rejoindre_en_tant_que_client()

    
    while True:
        conn, addr = server.accept()
        print("Connecté à", addr)
        clients.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def get_clients_addr():
    return [pseudos.get(client, "Inconnu") for client in clients if client in pseudos]

def lancer_partie():
    global jeu_instance, clients
    if len(clients) >= 2:  # Au moins 2 joueurs
        print(f"Lancement de la partie avec {len(clients)} joueurs")
        jeu_instance = Jeu(clients, pseudos)
        
        # Envoyer un signal à tous les clients pour lancer la partie
        message = json.dumps({
            "action": "start_game",
            "joueurs": list(pseudos.values())
        })
        
        for client in clients:
            try:
                client.send(message.encode('utf-8'))
            except:
                pass
        
        # Démarrer la logique de jeu
        threading.Thread(target=jeu_instance.jouer, daemon=True).start()

def handle_client(conn, addr):
    global clients, pseudos
    try:
        # Première connexion : récupérer le pseudo
        data = conn.recv(1024).decode('utf-8')
        pseudo = data.strip()
        pseudos[conn] = pseudo
        
        response = json.dumps({
            "action": "connected",
            "message": f"Bienvenue {pseudo}!"
        })
        conn.send(response.encode('utf-8'))
        
        # Boucle principale pour gérer les messages
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            
            try:
                message = json.loads(data)
                handle_game_message(conn, message)
            except json.JSONDecodeError:
                # Message simple (rétrocompatibilité)
                print(f"Reçu de {pseudo}:", data)
                if jeu_instance:
                    jeu_instance.traiter_message_joueur(conn, data)
                
    except Exception as e:
        print(f"Erreur avec {addr}: {e}")
    finally:
        conn.close()
        if conn in clients:
            clients.remove(conn)
        if conn in pseudos:
            del pseudos[conn]

def handle_game_message(conn, message):
    """Traite les messages de jeu structurés"""
    if jeu_instance and message.get("action") == "play_card":
        jeu_instance.recevoir_carte_jouee(conn, message.get("carte_index"))
    elif jeu_instance and message.get("action") == "choose_winner":
        jeu_instance.recevoir_choix_roi(conn, message.get("winner_pseudo"))
    else:
        print(f"Message non géré: {message}")

def diffuser_message(message):
    """Diffuse un message à tous les clients connectés"""
    message_str = json.dumps(message) if isinstance(message, dict) else message
    for client in clients[:]:  # Copie de la liste pour éviter les erreurs
        try:
            client.send(message_str.encode('utf-8'))
        except:
            clients.remove(client)