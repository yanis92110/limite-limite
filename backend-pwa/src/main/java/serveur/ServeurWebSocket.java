package serveur;

import org.java_websocket.server.WebSocketServer;
import org.java_websocket.WebSocket;
import org.java_websocket.handshake.ClientHandshake;
import controleur.ControleurServeur;
import modele.Joueur;

import java.net.InetSocketAddress;
import java.util.HashMap;
import java.util.Map;

public class ServeurWebSocket extends WebSocketServer {
    private ControleurServeur controleur;
    private Map<String, WebSocket> clients;
    private int nbJoueursAttendu;
    
    public ServeurWebSocket(int port, int nbJoueurs) {
        super(new InetSocketAddress(port));
        this.nbJoueursAttendu = nbJoueurs;
        this.clients = new HashMap<>();
        this.controleur = new ControleurServeur(this, nbJoueurs);
        
        // Désactiver le timeout (optionnel)
        setConnectionLostTimeout(0);
    }
    
    @Override
    public void onStart() {
        System.out.println("🚀 Serveur WebSocket prêt !");
    }
    
    @Override
    public void onOpen(WebSocket conn, ClientHandshake handshake) {
        System.out.println("🔗 Nouvelle connexion depuis: " + conn.getRemoteSocketAddress());
    }
    
    @Override
    public void onMessage(WebSocket conn, String message) {
        System.out.println("📨 Message reçu: " + message);
        
        try {
            if (message.startsWith("CONNEXION:")) {
                String nomJoueur = message.substring("CONNEXION:".length()).trim();
                
                // Vérifier si le nom est déjà pris
                if (clients.containsKey(nomJoueur)) {
                    conn.send("ERREUR:Pseudo déjà utilisé");
                    return;
                }
                
                // Ajouter le client
                clients.put(nomJoueur, conn);
                System.out.println("✅ " + nomJoueur + " connecté (" + clients.size() + "/" + nbJoueursAttendu + ")");
                
                // Ajouter le joueur à la partie
                Joueur joueur = new Joueur(nomJoueur);
                controleur.getPartie().ajouterJoueur(joueur);
                
                // Initialiser la main du joueur avec 10 cartes
                for (int i = 0; i < 10; i++) {
                    joueur.ajouterCarte(controleur.getPartie().getCartesBlanches().popCarte().getNom());
                }
                
                // Notifier tous les joueurs
                broadcast("ETAT:Joueur connecté: " + nomJoueur + " (" + clients.size() + "/" + nbJoueursAttendu + ")");
                
                // Si tous les joueurs sont là, démarrer la partie
                if (clients.size() == nbJoueursAttendu) {
                    System.out.println("🎮 Tous les joueurs sont connectés ! Démarrage...");
                    broadcast("DEBUT_PARTIE");
                    Thread.sleep(1000);
                    controleur.demarrerBoucleJeu();
                }
            } 
            else {
                // Trouver le nom du joueur qui a envoyé le message
                String nomJoueur = clients.entrySet().stream()
                    .filter(entry -> entry.getValue() == conn)
                    .map(Map.Entry::getKey)
                    .findFirst()
                    .orElse("Inconnu");
                
                if (!nomJoueur.equals("Inconnu")) {
                    controleur.recevoirAction(nomJoueur, message);
                }
            }
        } catch (Exception e) {
            System.err.println("❌ Erreur lors du traitement: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    @Override
    public void onClose(WebSocket conn, int code, String reason, boolean remote) {
        // Trouver et retirer le joueur déconnecté
        String nomJoueur = clients.entrySet().stream()
            .filter(entry -> entry.getValue() == conn)
            .map(Map.Entry::getKey)
            .findFirst()
            .orElse("Inconnu");
        
        clients.remove(nomJoueur);
        System.out.println("🔌 " + nomJoueur + " déconnecté (" + clients.size() + " restants)");
        
        if (!nomJoueur.equals("Inconnu")) {
            broadcast("ETAT:" + nomJoueur + " s'est déconnecté");
        }
    }
    
    @Override
    public void onError(WebSocket conn, Exception ex) {
        System.err.println("❌ Erreur WebSocket: " + ex.getMessage());
        ex.printStackTrace();
    }
    
    // Méthode pour envoyer à tous les clients
    public void broadcast(String message) {
        System.out.println("📢 Broadcast: " + message);
        for (WebSocket client : clients.values()) {
            if (client.isOpen()) {
                client.send(message);
            }
        }
    }
    
    // Méthode pour envoyer à un client spécifique
    public void envoyer(String nomJoueur, String message) {
        WebSocket client = clients.get(nomJoueur);
        if (client != null && client.isOpen()) {
            System.out.println("📤 Envoi à " + nomJoueur + ": " + message);
            client.send(message);
        } else {
            System.err.println("⚠️ Impossible d'envoyer à " + nomJoueur + " (déconnecté)");
        }
    }
}