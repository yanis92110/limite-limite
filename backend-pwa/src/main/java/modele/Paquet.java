package modele;

import java.io.File;
import java.util.ArrayList;
import java.util.Collections;

public class Paquet {
    private ArrayList<Carte> cartes;
    private int couleur = -1;
    
    public Paquet(int couleur) {
        this.cartes = new ArrayList<>();
        this.couleur = couleur;
        this.remplir();
    }
    
    public boolean paquetVide() {
        return this.cartes.isEmpty();
    }
    
    public void remplir() {
        File dir;
        if (couleur == 0) {
            // Cartes blanches - chemin relatif
            dir = new File("src/main/resources/img_blanches/");
        } else {
            // Cartes noires - chemin relatif
            dir = new File("src/main/resources/img_noires/");
        }
        
        if (!dir.exists()) {
            System.err.println("Erreur : dossier introuvable : " + dir.getAbsolutePath());
            return;
        }
        
        File[] liste = dir.listFiles();
        
        if (liste != null) {
            for (File f : liste) {
                if (f.getName().endsWith(".png")) {
                    cartes.add(new Carte(couleur, dir + "\\" + f.getName()));
                }
            }
        }
        
        Collections.shuffle(cartes);
    }
    
    public Carte popCarte() {
        if (this.cartes.isEmpty()) {
            this.remplir();
        }
        return this.cartes.removeLast();
    }
    
    public ArrayList<Carte> getCartes() {
        return cartes;
    }
    
    public void setCartes(ArrayList<Carte> cartes) {
        this.cartes = cartes;
    }
    
    public int getCouleur() {
        return couleur;
    }
    
    public void setCouleur(int couleur) {
        this.couleur = couleur;
    }
}