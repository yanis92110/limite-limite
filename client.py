import socket   
   
def rejoindre_serveur():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5000))  # connexion au serveur local

    pseudo = input("\nEntrer un Pseudo: \n")

    client.send(pseudo.encode())
    data = client.recv(1024).decode()
    print("Réponse du serveur:", data)