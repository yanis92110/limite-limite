import serveur.ServeurWebSocket;

public class Main {
    public static void main(String[] args){
        // Récupérer le port fourni par Render
        String portEnv = System.getenv("PORT");
        int port = (portEnv != null) ? Integer.parseInt(portEnv) : 10000;

        int nbJoueurs = 10; // nombre de joueurs max

        System.out.println("===========================================");
        System.out.println("  Aisselle Emeute Caca - Serveur PWA");
        System.out.println("===========================================");
        System.out.println();

        try {
            // Lancer le serveur WebSocket sur le port fourni
            ServeurWebSocket serveur = new ServeurWebSocket(port, nbJoueurs);
            serveur.start();

            System.out.println("Serveur WebSocket actif sur le port " + port);
            System.out.println("En attente de " + nbJoueurs + " joueurs...");
            System.out.println();
            System.out.println("Les joueurs peuvent se connecter via:");
            System.out.println("   ws://localhost:" + port + " (local)");
            System.out.println("   wss://limite-limite.onrender.com/ (Render)");
            System.out.println();
        } catch (Exception e) {
            System.err.println("Erreur au démarrage: " + e.getMessage());
            e.printStackTrace();
        }
    }
}