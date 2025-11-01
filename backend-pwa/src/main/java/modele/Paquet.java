package modele;

import java.io.File;
import java.net.URL;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Collections;

public class Paquet {
    private ArrayList<String> cartes;
    private int couleur = -1;
    
    @SuppressWarnings("OverridableMethodCallInConstructor")
    public Paquet(int couleur) {
        this.cartes = new ArrayList<>();
        this.couleur = couleur;
        this.remplir();
    }
    
    public boolean paquetVide() {
        return this.cartes.isEmpty();
    }
    
    public void remplir() {
        String path = (couleur == 0) ? "/img_blanches" : "/img_noires";

        try {
            // Récupère les ressources dans le classpath
            InputStream is = getClass().getResourceAsStream(path);
            if (is == null) {
                System.err.println("Erreur : dossier introuvable dans le classpath : " + path);
                return;
            }

            // Pour lister les fichiers dans un JAR, il faut utiliser ClassLoader + getResources
            var url = getClass().getResource(path);
            if (url == null) {
                System.err.println("Erreur : URL introuvable pour " + path);
                return;
            }

            File folder = new File(url.toURI());
            File[] liste = folder.listFiles();
            if (liste != null) {
                for (File f : liste) {
                    if (f.getName().endsWith(".png")) {
                        cartes.add(path + "/" + f.getName());
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        Collections.shuffle(this.cartes);
    }

    /**
     * Renvoie directement le chemin de la carte
     */
    public String popCarte() {
        if (this.cartes.isEmpty()) {
            this.remplir();
        }
        // Supprime et renvoie la dernière carte
        return this.cartes.remove(this.cartes.size() - 1);
    }

    
    public ArrayList<String> getCartes() {
        return cartes;
    }
    
    public void setCartes(ArrayList<String> cartes) {
        this.cartes = cartes;
    }
    
    public int getCouleur() {
        return couleur;
    }
    
    public void setCouleur(int couleur) {
        this.couleur = couleur;
    }
}