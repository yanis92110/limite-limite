package modele;

import java.util.ArrayList;

public class Joueur {
    private String nom;
    private ArrayList<String> cartes = new ArrayList<>();
    private int score = 0;
    private boolean roi = false;
    private boolean aJoue = false; // ✅ pour savoir si le joueur a joué pendant le tour
    private boolean isAdmin = false;

    public Joueur(String nom) {
        this.nom = nom;
    }

    public boolean isRoi() {
        return roi;
    }
    public boolean isAdmin() {
        return isAdmin;
    }
    public void setAdmin(boolean isAdmin) {
        this.isAdmin = isAdmin;
    }

    public void setRoi(boolean roi) {
        this.roi = roi;
    }

    public String getNom() {
        return nom;
    }

    public ArrayList<String> getCartes() {
        return cartes;
    }

    public void ajouterCarte(String c) {
        this.cartes.add(c);
    }

    public void viderCartes() {
        cartes.clear();
    }

    public void setCartes(ArrayList<String> cartes) {
        this.cartes = cartes;
    }

    public int getScore() {
        return score;
    }

    public void ajouterScore(int points) {
        score += points;
    }

    public boolean aJoue() {
        return aJoue;
    }

    public void setAJoue(boolean aJoue) {
        this.aJoue = aJoue;
    }

    @Override
    public String toString() {
        return nom + " (score: " + score + ")";
    }

	public void setNom(String nomJoueur) {
		// TODO Auto-generated method stub
		this.nom = nomJoueur;
	}
}
