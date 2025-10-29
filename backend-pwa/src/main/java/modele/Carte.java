package modele;

public class Carte {
	private int couleur;
	private String nom;
	
	public Carte(int c, String nom) {
		this.couleur = c;
		this.nom = nom;
	}
	public Carte(String nom) {
		this.nom = nom;
	}
	public int getCouleur() {
		return couleur;
	}
	public void setCouleur(int couleur) {
		this.couleur = couleur;
	}
	public String getNom() {
		return nom;
	}
	public void setNom(String nom) {
		this.nom = nom;
	}
}
