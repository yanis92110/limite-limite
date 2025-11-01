import serveur.ServeurWebSocket;
import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import java.io.IOException;
import java.net.InetSocketAddress;

public class Main {
    @SuppressWarnings("CallToPrintStackTrace")
    public static void main(String[] args) throws IOException {
        String portEnv = System.getenv("PORT");
        int port = (portEnv != null) ? Integer.parseInt(portEnv) : 8080;
        int nbJoueurs = 10; // Nombre de joueurs max
        HttpServer httpServer = HttpServer.create(new InetSocketAddress(port), 0);
        httpServer.createContext("/", new HttpHandler() {
            @Override
            public void handle(HttpExchange exchange) throws IOException {
                String response = "Serveur WebSocket actif !";
                exchange.sendResponseHeaders(200, response.getBytes().length);
                exchange.getResponseBody().write(response.getBytes());
                exchange.close();
            }
        });
        httpServer.start();
        
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