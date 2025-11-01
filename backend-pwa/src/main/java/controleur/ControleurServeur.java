package controleur;

import java.util.ArrayList;
import java.util.Random;

import app.Partie;
import modele.Carte;
import modele.Joueur;
import serveur.ServeurWebSocket;

public class ControleurServeur {
    private Partie partie;
    private ServeurWebSocket serveur;
    private boolean partieEnCours = false;
    
    public ControleurServeur(ServeurWebSocket serveur, int nbJoueurs) {
        this.serveur = serveur;
        this.partie = new Partie(nbJoueurs);
        System.out.println("✅ Partie créée avec " + nbJoueurs + " joueurs.");
    }
    public void nouvellePartie(int nbJoueurs) {
    	this.partie = new Partie(nbJoueurs);
    	System.out.println("🔄 Nouvelle partie créée avec " + nbJoueurs + " joueurs.");
    }

    public Partie getPartie() {
        return partie;
    }
    public boolean isPartieEnCours() {
        return partieEnCours;
    }
    public void setPartieEnCours(boolean b) {
        this.partieEnCours = b;
    }
    
    // ✅ À appeler explicitement depuis Serveur.lancerPartie()
    public void demarrerBoucleJeu() {
        partieEnCours = true;
        new Thread(() -> {
            try {
                bouclePartie();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }).start();
    }
    
    private void bouclePartie() throws InterruptedException {
        System.out.println("🎮 Début de la boucle de jeu");
        
        while (partieEnCours) {
            try {
                commencerTour();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            if(partie.isFinJeu()) {
            	partieEnCours = false;
                System.out.println("🏆 La partie est terminée !");
                Joueur gagnant = null;
                int scoreMax = -1;
            	for(Joueur j : partie.getJoueurs()) {
                    gagnant = (j.getScore() > scoreMax) ? j : gagnant;
                    scoreMax = Math.max(j.getScore(), scoreMax);
            		if(j.getScore()>=partie.getScoreGagnant()) {
            			serveur.broadcast("VICTOIRE:"+j.getNom());
            			System.out.println("🏆 Le gagnant est : "+j.getNom());
            		}
            	}
            	
        }
    }
    Thread.sleep(700); // Pause avant de recommencer un tour
    serveur.broadcast("RESET");
    }
    private void envoyerMainsAuxJoueurs() {
    	//Les cartes envoyées sont cliquables
        for (Joueur j : partie.getJoueurs()) {
        	envoyerMainJoueur(j.getNom());
        }
    }
    private void envoyerMainJoueur(String nomJoueur) {
    	Joueur j = partie.getJoueurParNom(nomJoueur);
    	StringBuilder sb = new StringBuilder("MAIN:");
        for (String c : j.getCartes()) {
            sb.append(c).append(",");
        }

        // Supprimer la dernière virgule s’il y en a une
        if (sb.length() > 5) sb.deleteCharAt(sb.length() - 1);

        // Envoyer uniquement au joueur concerné
        serveur.envoyer(j.getNom(), sb.toString());
    }
    	
    

    
    private void commencerTour() throws InterruptedException {
        if(!partieEnCours){
            serveur.broadcast("RESET");
            return;
        }
        for(Joueur j : partie.getJoueurs()) {
        	if(j.getScore()>=partie.getScoreGagnant()) {
        		partie.setFinJeu(true);
                return;
        	}
        }
    	//partie.setRoi(partie.getJoueurParNom("serveur"));
        serveur.broadcast("NOUVEAU_TOUR:"+partie.getTour());
        Joueur roi = partie.getRoi();
        System.out.println("NOUVEAU TOUR : Tour "+partie.getTour());
        
        if (roi == null) {//Rentre si premier tour
        	
    		//Choix aléatoire du roi
        	
    		Random randomNumbers = new Random();
    		var value = randomNumbers.nextInt(this.partie.getJoueurs().size());
    		
    		roi = this.getPartie().getJoueurs().get(value);
    		partie.setRoi(roi);

        }
            // ✅ IMPORTANT : Réinitialiser tous les statuts
        for(Joueur j : partie.getJoueurs()) {
            j.setRoi(false);  // Tout le monde perd le statut
            j.setAJoue(false);
        }
        roi.setRoi(true);
            

        // 🃏 Carte centrales
        Carte carteCentrale = partie.getCartesNoires().popCarte();
        serveur.broadcast("CARTE_CENTRALE:" + carteCentrale.getNom());
        
        //envoyerMainsAuxJoueurs();
        
        //Attention les cartes sont cliquables
        
        //Envoie de l'etat ROI au roi
        
                // Puis envoyer les statuts
        for(Joueur j : partie.getJoueurs()) {
            if(j.isRoi()) {
                serveur.envoyer(j.getNom(),"VOUS_ETES_ROI");
                serveur.envoyer(j.getNom(), "ETAT:Vous êtes roi ! Attente des joueurs...");
            }
            else {
                serveur.envoyer(j.getNom(), "ETAT:A votre tour de jouer !");
            }
        }
        serveur.broadcast("ROI:"+roi.getNom());

        
        // ✅ Envoyer la main à TOUT LE MONDE (même le roi, pour qu'il voie ses cartes mises à jour)
        for(Joueur j : partie.getJoueurs()) {
            envoyerMainJoueur(j.getNom());
        }




        
        System.out.println("⏳ Attente des réponses des joueurs...");
        if(!partieEnCours){
            serveur.broadcast("RESET");
            return;
        }
        
        // ⏳ Attendre que tous jouent
        attendreReponses();
        
        for(Joueur j : partie.getJoueurs()) {
        	if(!j.isRoi()) {
        		serveur.envoyer(j.getNom(), "ETAT:Le roi choisi le vainqueur...");
        	}
        	//Cas roi traiter dans la methode traiterCartesBlanches
        }
        
        // 🎯 Traiter les résultats
        traiterCartesBlanches();

        partie.addTour();
        Thread.sleep(3000); // Pause entre les tours
    }
    
    private void attendreReponses() throws InterruptedException {
        int timeout = 0;
        
        // Compter combien de joueurs doivent jouer
        long nbJoueursAAttendre = partie.getJoueurs().stream()
                .filter(j -> !j.isRoi())
                .count();
        
        System.out.println("⏳ Attente de " + nbJoueursAAttendre + " joueur(s)...");
        
        while (!tousOntJoue() && timeout < 600) { // 60 secondes max

            Thread.sleep(100);
            timeout++;
            
            // Debug tous les 10 coups (1 seconde)
            if (timeout % 10 == 0) {
                long nbJoueurs = partie.getJoueurs().stream()
                        .filter(j -> !j.isRoi())
                        .filter(Joueur::aJoue)
                        .count();
                System.out.println("  ⏱️ " + nbJoueurs + "/" + nbJoueursAAttendre + " ont joué (" + (timeout/10) + "s)");
                if(!partieEnCours){
                    serveur.broadcast("RESET");
                    return;
                }
            }
        }
        
        if (timeout >= 600) {
            System.out.println("⚠️ Timeout atteint !");
        } else {
            System.out.println("✅ Tous les joueurs ont joué !");
        }
    }
    
    private boolean tousOntJoue() {
        // Tous les joueurs sauf le roi doivent avoir joué
        boolean resultat = partie.getJoueurs().stream()
                .filter(j -> !j.equals(partie.getRoi()))
                .allMatch(Joueur::aJoue);
        
        return resultat;
    }

    
    private void traiterCartesBlanches() throws InterruptedException{
        ArrayList<String> cartesJouees = partie.getCartesBlanchesActuelles();

        String cartesStr = String.join(",", cartesJouees);
        
        
        serveur.broadcast("RESULTAT:" + cartesStr);
        
        serveur.envoyer(partie.getRoi().getNom(),"CHOISIR");
        int timeout = 0;
        while(!partie.getRoi().aJoue() && timeout <600) {
            Thread.sleep(100);
            timeout++;
            if(!partieEnCours){
                serveur.broadcast("RESET");
                return;
            }
        }
        if(timeout>=600) {
            System.out.println("Time out atteint");
            // Choisir une carte aléatoirement comme gagnante
            if (cartesJouees.isEmpty()) {
                System.out.println("⚠️ Aucun choix possible : aucune carte jouée.");
            } else {
                Random rdm = new Random();
                int indexChoisi = rdm.nextInt(cartesJouees.size());
                String carteChoisie = cartesJouees.get(indexChoisi);
                System.out.println("🎲 Choix aléatoire : index=" + indexChoisi + " -> " + carteChoisie);
                
                // On attend le format "nomCarte#nomJoueur"
                String[] parts = carteChoisie.split("#", 2);
                String nomCarte = parts.length > 0 ? parts[0] : carteChoisie;
                String nomJoueurGagnant = parts.length > 1 ? parts[1] : null;
                
                if (nomJoueurGagnant != null) {
                    System.out.println("🏆 Joueur gagnant (aléatoire) : " + nomJoueurGagnant);
                    partie.getJoueurParNom(nomJoueurGagnant).ajouterScore(1);
                    
                    
                    // Notifier tous les clients du résultat
                    serveur.broadcast("ETAT:" + "GAGNANT : "+ nomJoueurGagnant);
                    serveur.envoyer(nomJoueurGagnant, "ETAT:Vous avez gagné ce tour (choix aléatoire) !");
                    changerRoi(nomJoueurGagnant);
                } else {
                    System.out.println("⚠️ Impossible de déterminer le joueur gagnant depuis la carte : " + carteChoisie);
                }
            }
            
        } else {
            System.out.println("✅ Le roi a choisi un gagnant.");
        }
        
        // TODO : Déterminer le gagnant du tour (si besoin d'autres règles)
        
        Thread.sleep(200);
        
        partie.viderCartesBlanches();
        serveur.broadcast("RETIRER_CARTES_JOUEES");
        Thread.sleep(100);
    }
    
    private void changerRoi(String nomJoueur) {
    	
    	partie.getRoi().setRoi(false);
    	
    	partie.setRoi(partie.getJoueurParNom(nomJoueur));
    	partie.getJoueurParNom(nomJoueur).setRoi(true);
    	
    }
    
    public void recevoirAction(String joueurNom, String action) {
        System.out.println("📥 Action reçue de " + joueurNom + " : " + action);
        
        if (action.startsWith("JOUER_CARTE:")) {
        	String nomCarte = action.split(":",2)[1];
            Joueur joueur = partie.getJoueurParNom(joueurNom);
            String nomCarteSansJoueur = nomCarte.split("#")[0];
            String carteAvecNom = nomCarte + "#" + joueurNom;  // ← Important !

                joueur.setAJoue(true);
                partie.ajouterCarteBlanche(carteAvecNom);
                joueur.getCartes().remove(nomCarteSansJoueur);
                
                // Piocher une nouvelle carte
                joueur.ajouterCarte(partie.getCartesBlanches().popCarte().getNom());
                
                System.out.println("✅ " + joueurNom + " a joué sa carte");
            
        }
        else if (action.startsWith("CHOISIR_GAGNANT:")) {
        	
            String nomCarte = action.substring("RESULTAT:".length());
        	nomCarte = action.split("#")[0];
        	String nomJoueurGagnant = action.split("#")[1];
        	
            System.out.println("GAGNANT : "+nomJoueurGagnant);
            serveur.broadcast("CARTE_GAGNANTE:"+nomCarte);
            serveur.broadcast("ETAT:"+"GAGNANT : "+nomJoueurGagnant);
            serveur.envoyer(nomJoueurGagnant, "ETAT:Vous avez gagné ce tour! gg");
            serveur.envoyer(nomJoueurGagnant,"VICTOIRE_TOUR");
            partie.getJoueurParNom(nomJoueurGagnant).ajouterScore(1);
            
            changerRoi(nomJoueurGagnant);
        	
        }
        else if (action.startsWith("ADMIN:")) {
        	String commande = action.split(":",2)[1];
        	if(commande.equals("START_GAME")) {
        		if(!partieEnCours) {
        			System.out.println("🚀 Admin -> Démarrage de la partie");
        			demarrerBoucleJeu();
        		} else {
        			System.out.println("⚠️ La partie est déjà en cours !");
                    serveur.envoyer(joueurNom, "ALERTE:La partie est déjà en cours !");
        		}
        	}
        	else if(commande.equals("RESET_GAME")) {
        		System.out.println("🔁 Admin -> Réinitialisation de la partie");
        		partieEnCours = false;
        		
                int nbJoueurs = partie.getJoueurs().size();
                nouvellePartie(nbJoueurs);
        	}
            else if(commande.startsWith("LOGIN:")){
                String nomJoueur = commande.split(":",2)[1];
                Joueur j = partie.getJoueurParNom(nomJoueur);
                if(j != null) {
                    j.setAdmin(true);
                    System.out.println("🛠️ " + nomJoueur + " est maintenant admin.");
                }
            }
        }
    }
}