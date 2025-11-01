package app;

import java.util.ArrayList;
import java.util.Collections;

import modele.Joueur;
import modele.Paquet;

public class Partie {
	private Paquet cartesBlanches, cartesNoires;
	private ArrayList<Joueur> joueurs;
	private ArrayList<String> cartesBlanchesActuelles;
	private Joueur roi = null;
	private int nbJoueurs;
	private int tour = 0;
	private boolean finJeu = false;
	private int scoreGagnant = 5; //Score a atteindre pour gagner la partie
	
	public Partie(int nbJoueurs) {
		

		//boolean value = randomNumbers.nextBoolean();
		
		this.joueurs = new ArrayList<Joueur>();
		this.cartesBlanchesActuelles = new ArrayList<String>();
		this.cartesBlanches = new Paquet(0);
		this.cartesNoires = new Paquet(1);
		this.nbJoueurs = nbJoueurs;

		
	}
	public int getScoreGagnant() {
		return this.scoreGagnant;
	}
	public void setScoreGagnant(int score) {
		this.scoreGagnant = score;
	}
	public int getTour() {
		return this.tour;
	}
    public void ajouterJoueur(Joueur joueur) {
        if (joueurs.size() < nbJoueurs) {
            joueurs.add(joueur);
        }
    }
	public void addTour() {
		this.tour++;
	}
	
	public Paquet getCartesBlanches() {
		return cartesBlanches;
	}
	public void viderCartesBlanches() {
		this.cartesBlanchesActuelles.clear();
	}
	public Joueur getJoueurParNom(String nom) {
	    for (Joueur j : this.joueurs) {
	        if (j.getNom().equals(nom)) {
	            return j;
	        }
	    }
	    return null; // si aucun joueur trouvé
	}

	public void ajouterCarteBlanche(String c) {
		this.cartesBlanchesActuelles.add(c);
	}
	public void shuffleCartesBlanchesActuelles() {
		Collections.shuffle(this.cartesBlanchesActuelles);
	}
	public void setCartesBlanches(Paquet cartesBlanches) {
		this.cartesBlanches = cartesBlanches;
	}
	public Paquet getCartesNoires() {
		return cartesNoires;
	}
	public void setCartesNoires(Paquet cartesNoires) {
		this.cartesNoires = cartesNoires;
	}
	public ArrayList<Joueur> getJoueurs() {
		return joueurs;
	}
	public void setJoueurs(ArrayList<Joueur> joueurs) {
		this.joueurs = joueurs;
	}

	public ArrayList<String> getCartesBlanchesActuelles() {
	    return cartesBlanchesActuelles;
	}

	public void setCartesBlanchesActuelles(ArrayList<String> cartesBlanchesActuelles) {
		this.cartesBlanchesActuelles = cartesBlanchesActuelles;
	}

	public boolean isFinJeu() {
		return finJeu;
	}

	public void setFinJeu(boolean finJeu) {
		this.finJeu = finJeu;
	}

	public Joueur getRoi() {
		return roi;
	}

	public void setRoi(Joueur roi) {
		this.roi = roi;
	}

	
}
