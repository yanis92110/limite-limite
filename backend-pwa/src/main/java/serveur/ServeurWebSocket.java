package serveur;

import java.net.InetSocketAddress;
import java.util.HashMap;
import java.util.Map;

import org.java_websocket.WebSocket;
import org.java_websocket.handshake.ClientHandshake;
import org.java_websocket.server.WebSocketServer;

import controleur.ControleurServeur;
import modele.Joueur;

public class ServeurWebSocket extends WebSocketServer {
    private final ControleurServeur controleur;
    private final Map<String, WebSocket> clients;
    @SuppressWarnings("FieldMayBeFinal")
    private int nbJoueursAttendu; //Pas final au cas ou on ajoute le bouton plus tard la
    
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
    @SuppressWarnings("UseSpecificCatch")
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
                if(controleur.getPartie().isFinJeu()) {
                    conn.send("ERREUR:Partie déjà commencée");
                    
                    // Envoyer l'alerte uniquement aux admins
                    for (Map.Entry<String, WebSocket> entry : clients.entrySet()) {
                        WebSocket client = entry.getValue();
                        String playerName = entry.getKey();
                        if (client.isOpen() && controleur.getPartie().getJoueurParNom(playerName).isAdmin()) {
                            client.send("ALERTE:Un joueur a tenté de rejoindre une partie en cours.");
                        }
                    }
                    return;
                }
                
                // Ajouter le client
                clients.put(nomJoueur, conn);
                System.out.println("✅ " + nomJoueur + " connecté (" + clients.size() + "/" + nbJoueursAttendu + ")");
                
                // Ajouter le joueur à la partie
                Joueur joueur = new Joueur(nomJoueur);
                controleur.getPartie().ajouterJoueur(joueur);
                
                // Initialiser la main du joueur avec 8 cartes
                for (int i = 0; i < 8; i++) {
                    joueur.ajouterCarte(controleur.getPartie().getCartesBlanches().popCarte());
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
            else if(message.startsWith("ADMIN:")){
                String part = message.substring("ADMIN:".length());
                if(part.startsWith("START_GAME")){
                    System.out.println("🚀 Démarrage de la partie demandé par l'admin.");
                    controleur.demarrerBoucleJeu();
                }
                else if(part.startsWith("RESET_GAME")){
                    System.out.println("🔄 Réinitialisation de la partie demandé par l'admin.");
                    controleur.setpartieReinitialisee(true);
                    controleur.getPartie().setFinJeu(true);
                    controleur.nouvellePartie(nbJoueursAttendu);
                    
                    Thread.sleep(1000);
                    controleur.setpartieReinitialisee(false);
                    broadcast("RESET");
                }
                else if(part.startsWith("SET_SCORE_GAGNANT:")){
                    String scoreStr = part.substring("SET_SCORE_GAGNANT:".length()).trim();
                    try {
                        int score = Integer.parseInt(scoreStr);
                        controleur.getPartie().setScoreGagnant(score);
                        System.out.println("😹 Score gagnant mis à jour à " + score + " par l'admin.");
                    } catch (NumberFormatException e) {
                        System.err.println("⚠️ Valeur de score invalide reçue de l'admin: " + scoreStr);
                    }
                }
                else if(part.startsWith("LOGIN:")){
                    String nomAdmin = part.substring("LOGIN:".length()).trim();
                    Joueur joueur = controleur.getPartie().getJoueurParNom(nomAdmin);
                    if(joueur != null) {
                        joueur.setAdmin(true);
                        System.out.println("🔑 " + nomAdmin + " est maintenant admin.");
                        envoyer(nomAdmin, "ETAT:Vous êtes connecté en tant qu'admin.");
                    } else {
                        System.err.println("⚠️ Tentative de connexion admin échouée pour " + nomAdmin + " (joueur non trouvé).");
                        envoyer(nomAdmin, "ERREUR:Échec de la connexion admin (joueur non trouvé).");
                    }
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
    }
    @Override
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