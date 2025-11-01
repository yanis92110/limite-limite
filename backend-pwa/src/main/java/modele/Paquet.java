package modele;

import java.io.IOException;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Enumeration;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;

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
    

    @SuppressWarnings({"ConvertToTryWithResources", "CallToPrintStackTrace"})
    public void remplir() {
        @SuppressWarnings("unused")
        String path = (couleur == 0) ? "img_blanches" : "img_noires";
        cartes.clear();

        try {
            // Récupérer le chemin du JAR
            String jarPath = getClass().getProtectionDomain().getCodeSource().getLocation().toURI().getPath();
            JarFile jar = new JarFile(jarPath);

            Enumeration<JarEntry> entries;
            entries = jar.entries();
            while (entries.hasMoreElements()) {
                JarEntry entry = entries.nextElement();
                String name = entry.getName();
                if (name.startsWith("img_blanches/") && couleur == 0 && name.endsWith(".png")) {
                    cartes.add("/" + name);
                } else if (name.startsWith("img_noires/") && couleur == 1 && name.endsWith(".png")) {
                    cartes.add("/" + name);
                }
            }
            jar.close();
        } catch (IOException | URISyntaxException e) {
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