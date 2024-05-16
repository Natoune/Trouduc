import os

import socketio.server as Sio

from classes.joueur import Joueur


class Manche:
    def __init__(self, sio: Sio.Server, id_salon: str, joueurs: list[Joueur]):
        self.sio = sio
        self.id_salon = id_salon
        self.joueurs = joueurs
        self.roles_assignes = [None, None, None, None]
        self.roles_restants = ["🤡", "📝", "🥈", "👑"]
        self.j = 0
        self.compteur = 0
        self.derniere_valeur = 0
        self.dernier_coup = []
        self.nb_cartes = 0
        self.premier_tour = True
        self.suite = 0

        self.running_joueurs = [0, 1, 2, 3]

    def reset(self):
        self.derniere_valeur = 0
        self.dernier_coup = []
        self.nb_cartes = 0
        self.suite = 0
        self.compteur = 0
        # self.running_joueurs = [0, 1, 2, 3]
        self.running_joueurs = [i for i in range(
            4) if len(self.joueurs[i].main) > 0]
        self.premier_tour = True

    def jouer_cartes(self, cartes):
        joueur = self.joueurs[self.j]

        # La main du joueur est vide
        if len(joueur.main) == 0:
            return {
                "status": 400,
                "message": "Vous n'avez plus de cartes",
            }

        # Passer son tour (carte -1)
        if -1 in cartes:
            if self.premier_tour:
                return {
                    "status": 400,
                    "message": "Vous ne pouvez pas passer votre tour",
                }

            # On note le joueur comme ayant passé son tour
            j_id = self.running_joueurs.index(self.j)
            del self.running_joueurs[j_id]

            self.suite = 0  # Casse la suite en cours

            if len(self.running_joueurs) == 0:
                self.reset()
                return {
                    "status": 200,
                    "message": "Tour passé",
                }

            self.j = (self.j + 1) % 4

            return {
                "status": 200,
                "message": "Tour passé",
            }

        valeur = 0

        # Nombre de cartes à jouer
        if self.nb_cartes > 0 and len(cartes) != self.nb_cartes:
            return {
                "status": 400,
                "message": f"Vous devez jouer {self.nb_cartes} carte{'s' if self.nb_cartes > 1 else ' seulement'} !",
            }

        # Vérification de chaque carte
        for carte in cartes:
            # Carte en main
            if not 0 <= carte < len(joueur.main):
                return {
                    "status": 400,
                    "message": "Carte invalide",
                }

            # Carte de même valeur que les autres (la première carte est la référence)
            if valeur not in (0, joueur.main[carte][1]):
                return {
                    "status": 400,
                    "message": "Vous devez jouer des cartes de même valeur !",
                }

            # Récupération de la valeur de la carte
            valeur = joueur.main[carte][1]

        # Le premier tour détermine le nombre de cartes à jouer
        if self.premier_tour:
            self.nb_cartes = len(cartes)
            self.compteur = self.nb_cartes

        # Établir la puissance de la carte
        try:
            valeur = int(valeur)
        except ValueError:
            valeur = ["J", "Q", "K", "A"].index(valeur) + 11

        # Suite en cours (le joueur doit jouer des cartes de même valeur que précédemment)
        if self.suite > 0 and valeur != self.derniere_valeur:
            return {
                "status": 400,
                "message": "Suite de cartes ! Vous devez jouer des cartes de même valeur que précédemment ou passer votre tour.",
            }

        # Carte 2 (remporte le tour)
        if valeur == 2:
            # Interdit de jouer un 2 comme dernière carte
            if len(joueur.main) - len(cartes) < 1:
                # Si c'est le cas, le joueur est désigné comme Trouduc (ou le moins bon rôle restant si un Trouduc a déjà été désigné)
                self.roles_assignes[self.j] = self.roles_restants[0]
                del self.roles_restants[0]

            cartes = cartes[::-1]
            for carte in cartes:
                del joueur.main[carte]

            self.reset()

            # self.j reste inchangé, le joueur rejoue

            return {
                "status": 200,
                "message": "Cartes jouées",
            }

        # Carte inférieure à la précédente
        if valeur < self.derniere_valeur:
            return {
                "status": 400,
                "message": "Vous devez jouer des cartes de valeurs supérieures à la précédente !",
            }

        # Carte identique à la précédente (suite de cartes de même valeur)
        if valeur == self.derniere_valeur and not self.premier_tour:
            self.suite += 1
            self.compteur += self.nb_cartes
        else:
            self.compteur = self.nb_cartes

        # Mise à jour des informations de la manche
        self.derniere_valeur = valeur
        self.dernier_coup = [joueur.main[carte] for carte in cartes]
        self.premier_tour = False
        # self.running_joueurs = [0, 1, 2, 3]
        self.running_joueurs = [i for i in range(
            4) if len(self.joueurs[i].main) > 0]

        # Suppression des cartes de la main du joueur
        cartes = cartes[::-1]  # Inversion pour éviter les problèmes d'index
        for carte in cartes:
            del joueur.main[carte]

        # Màj du joueur
        self.joueurs[self.j] = joueur

        # Remporte le tour
        if len(joueur.main) == 0:
            self.roles_assignes[self.j] = self.roles_restants[-1]
            del self.roles_restants[-1]
            self.reset()

        # Carré
        if self.compteur == 4:
            self.reset()
        else:  # Joueur suivant
            self.j = (self.j + 1) % 4

        # Fin de la manche
        if len(self.roles_restants) == 1:
            self.roles_assignes[self.j] = self.roles_restants[-1]

            return {
                "status": 100,
                "message": "Cartes jouées",
            }

        return {
            "status": 200,
            "message": "Cartes jouées",
        }

    def infos(self):
        return {
            "nb_cartes": self.nb_cartes,
            "dernier_coup": self.dernier_coup,
            "premier_tour": self.premier_tour,
            "suite": self.suite,
            "debug": {
                "j": self.j,
                "compteur": self.compteur,
                "derniere_valeur": self.derniere_valeur,
                "roles_assignes": self.roles_assignes,
                "roles_restants": self.roles_restants,
                "running_joueurs": self.running_joueurs,
            } if os.environ["NODE_ENV"] == "development" else None,
        }
