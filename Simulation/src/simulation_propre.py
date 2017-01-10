import time
import random
from lieu_ferme import LieuFerme
from personne import Personne
from obstacle_rectangulaire import ObstacleRectangulaire
from espace import Espace
from pymunk.vec2d import Vec2d
import pygame
import pymunk.pygame_util

class ConstructeurSalle(object):
       
    def __init__(self, donnees_simulation):
        self.donnees_simulation = donnees_simulation
        
        self.espace = Espace()
        self.ajouterLieuFerme(self.espace, **self.donnees_simulation['lieu_ferme'])
        self.ajouterObstacles(self.espace, **self.donnees_simulation['obstacles'])
        
    
    def ajouterLieuFerme(self, espace, salle_hauteur=None, salle_largeur=None,
            porte_largeur=None, porte_position=None):

        espace.ajouterLieuFerme(LieuFerme(salle_largeur, salle_hauteur, Vec2d(50, 50), porte_position, porte_largeur))
    
    def ajouterObstacles(self,espace, obstacle_hauteur=None, 
            obstacle_largeur=None, obstacle_distance_intermediaire=None,
            mur_rang_distance=None, obstacle_gauche_position_premier=None,
            obstacle_droit_position_premier=None):

        position_gauche_y = obstacle_gauche_position_premier
        position_droit_y = obstacle_droit_position_premier
        
        while position_gauche_y + 50 <=self.espace.lieu_ferme.hauteur :
            position_gauche = 50 + mur_rang_distance, position_gauche_y

            obstacle_gauche = ObstacleRectangulaire(obstacle_hauteur,
                obstacle_largeur, position_gauche)
            espace.ajouterObstacle(obstacle_gauche)

            position_gauche_y += obstacle_distance_intermediaire
            
        
        while position_droit_y + 50 <= self.espace.lieu_ferme.hauteur :
            position_droit_x = 50 + self.espace.lieu_ferme.largeur / 2 + mur_rang_distance
            position_droit = position_droit_x, position_droit_y
            
            obstacle_droit = ObstacleRectangulaire(obstacle_hauteur,
                obstacle_largeur, position_droit)
            espace.ajouterObstacle(obstacle_droit)

            position_droit_y += obstacle_distance_intermediaire

class EcouteurPersonne(object):

    def __init__(self, personne, action):
        self.personne = personne
        self.action = action
        self.personne_deja_sortie = False

    def ecouter(self, temps):
        if not self.personne_deja_sortie and self.personne.estSortie():
            self.personne_deja_sortie = True
            self.executerAction(temps)

    def executerAction(self, temps):
        #Seul moyen d'appeler la fonction self.action sans passer self comme
        #premier argument
        _action = self.action
        _action(temps)

class ConstructeurSimulation(object):

    def __init__(self, donnees_simulation, action_sortie):
        constructeur_salle = ConstructeurSalle(donnees_simulation)
        self.simulation = Simulation(constructeur_salle.espace, donnees_simulation['mise_a_jour_par_seconde'])
        self.contruirePersonneEtEcouteur(action_sortie, **donnees_simulation['personnes'])

    def contruirePersonneEtEcouteur(self, action_sortie, nombre=0):
        #Pour le moment on met un ecouteur sur chaque personne
        for _ in range(nombre):
            personne = Personne(Vec2d(random.randint(60, 40 + self.simulation.espace.lieu_ferme.largeur),
                random.randint(60, 40 + self.simulation.espace.lieu_ferme.hauteur)), self.simulation.espace)
            self.simulation.ecouteurs.append(EcouteurPersonne(personne, action_sortie))
            self.simulation.espace.ajouterPersonne(personne)

class Simulation(object):

    AUCUN = 0x0
    ARRET = 0x1
    
    def __init__(self, espace, mise_a_jour_par_seconde):
        self.espace = espace
        self.mise_a_jour_par_seconde = mise_a_jour_par_seconde
        self.ecouteurs = []
        self.action_mise_a_jour = lambda simulation: None
        self.en_marche = False

    def mettreAJour(self):
        self.espace.avancer(1 / self.mise_a_jour_par_seconde)
        self.temps_depuis_lancement = time.time() - self.debut_lancement
        for ecouteur in self.ecouteurs:
            ecouteur.ecouter(self.temps_depuis_lancement)
        commande = self.action_mise_a_jour(self)
        self.executerCommande(commande)

    def executerCommande(self, commande):
        if commande & Simulation.ARRET:
            self.en_marche = False

    def lancer(self):
        self.debut_lancement = time.time()
        self.temps_depuis_lancement = 0
        self.en_marche = True
        while self.en_marche:
            self.mettreAJour()
