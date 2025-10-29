import serveur.ServeurWebSocket;

public class Main {
    public static void main(String[] args) {
        int port = 8080;
        int nbJoueurs = 3;
        
        System.out.println("===========================================");
        System.out.println("  Aisselle Emeute Caca - Serveur PWA");
        System.out.println("===========================================");
        System.out.println();
        
        try {
            ServeurWebSocket serveur = new ServeurWebSocket(port, nbJoueurs);
            serveur.start();
            
            System.out.println("Serveur demarre sur le port " + port);
            System.out.println("En attente de " + nbJoueurs + " joueurs...");
            System.out.println();
            System.out.println("Les joueurs peuvent se connecter via:");
            System.out.println("   ws://localhost:" + port);
            System.out.println();
            
        } catch (Exception e) {
            System.err.println("Erreur au demarrage: " + e.getMessage());
            e.printStackTrace();
        }
    }
}