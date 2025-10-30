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
    
    public Partie getPartie() {
        return partie;
    }
    
    // ✅ À appeler explicitement depuis Serveur.lancerPartie()
    public void demarrerBoucleJeu() {
        partieEnCours = true;
        new Thread(this::bouclePartie).start();
    }
    
    private void bouclePartie() {
        System.out.println("🎮 Début de la boucle de jeu");
        
        while (partieEnCours) {
            try {
                commencerTour();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
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
    	//partie.setRoi(partie.getJoueurParNom("serveur"));
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
        


        
        // ✅ Envoyer la main à TOUT LE MONDE (même le roi, pour qu'il voie ses cartes mises à jour)
        for(Joueur j : partie.getJoueurs()) {
            envoyerMainJoueur(j.getNom());
        }

        // Puis envoyer les statuts
        for(Joueur j : partie.getJoueurs()) {
            if(j.isRoi()) {
                serveur.envoyer(j.getNom(),"VOUS_ETES_ROI");
                serveur.envoyer(j.getNom(), "ETAT:Vous êtes roi ! Attente des joueurs... isRoi ?" + j.isRoi());
            }
            else {
                serveur.envoyer(j.getNom(), "ETAT:A votre tour de jouer ! isRoi ?" + j.isRoi());
            }
        }
        serveur.broadcast("ROI:"+roi.getNom());


        
        System.out.println("⏳ Attente des réponses des joueurs...");

        
        // ⏳ Attendre que tous jouent
        attendreReponses();
        
        for(Joueur j : partie.getJoueurs()) {
        	if(!j.isRoi()) {
        		serveur.envoyer(j.getNom(), "ETAT:Le roi choisi le vainqueur...isRoi ?" + j.isRoi());
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
        
        // 🔍 DEBUG : Vérifier le contenu
        /*
        System.out.println("🔍 Debug : cartesJouees contient " + cartesJouees.size() + " éléments");
        for (int i = 0; i < cartesJouees.size(); i++) {
            System.out.println("  [" + i + "] = '" + cartesJouees.get(i) + "'");
        }*/
        
        // ✅ Convertir la liste en String avec virgules
        String cartesStr = String.join(",", cartesJouees);
        
        //System.out.println("📊 Cartes jouées : " + cartesStr);
        
        serveur.broadcast("RESULTAT:" + cartesStr);
        
        serveur.envoyer(partie.getRoi().getNom(),"CHOISIR");
        int timeout = 0;
        while(!partie.getRoi().aJoue() && timeout <600) {
            Thread.sleep(100);
            timeout++;
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
            serveur.broadcast("ETAT:"+"GAGNANT : "+nomJoueurGagnant);
            serveur.envoyer(nomJoueurGagnant, "ETAT:Vous avez gagné ce tour! gg");
            partie.getJoueurParNom(nomJoueurGagnant).ajouterScore(1);
            
            changerRoi(nomJoueurGagnant);
        	
        }
    }
}