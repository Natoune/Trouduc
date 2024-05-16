from random import randint

import socketio.server as Sio

from classes.joueur import Joueur
from classes.manche import Manche


class Salon:
    def __init__(self, sio: Sio.Server, id_salon: str, nom: str, nom_createur: str, sid: str):
        self.sio = sio
        self.id = id_salon
        self.nom = nom
        self.manche = None
        self.numero_manche = 0
        self.echanges_effectues = 0
        self.createur = sid
        self.attente = True
        self.attente_echanges = False
        self.cartes = self.__shuffle(self.__gen_cartes())
        self.joueurs: list[Joueur] = [None for _ in range(4)]
        self.joueurs[0] = Joueur(
            sid,
            nom=nom_createur,
            main=self.cartes[0:13],
            role="",
            createur=True
        )

    def debut_manche(self):
        if self.numero_manche > 0 and self.echanges_effectues < 2:
            # Distribution des cartes au hasard
            jeu = self.__shuffle(self.cartes)

            for i in range(4):
                self.joueurs[i].main = jeu[i * 13: (i + 1) * 13]

            # Distribution automatique des cartes les plus fortes pour les rôles du trouduc et du secrétaire
            distribution_automatique, dons = self.__distribuer_cartes(jeu)

            self.attente_echanges = True
            self.sio.emit("update_salon", self.__infos_salon(), room=self.id)

            # Demander les 2 cartes à donner par le président au trouduc
            self.sio.emit("donner_cartes", {
                "main": self.joueurs[3].main,
                "nb": 2,
            }, to=self.joueurs[3].sid)

            # Demander la carte à donner par le vice-président au secrétaire
            self.sio.emit("donner_cartes", {
                "main": self.joueurs[2].main,
                "nb": 1,
            }, to=self.joueurs[2].sid)

            # Jouer les animations de dons de cartes forcés pour le secrétaire et le trouduc
            self.sio.emit("donner_cartes", {
                "main": self.joueurs[0].main,
                "dons": dons[0],
                "nb": 2,
            }, to=self.joueurs[0].sid)

            self.sio.emit("donner_cartes", {
                "main": self.joueurs[1].main,
                "dons": dons[1],
                "nb": 1,
            }, to=self.joueurs[1].sid)

            for i in range(4):
                self.joueurs[i].main = distribution_automatique[i]
        else:
            self.attente = False
            self.manche = Manche(
                sio=self.sio, id_salon=self.id, joueurs=self.joueurs)
            self.numero_manche += 1

            self.sio.emit("update_salon", self.__infos_salon(), room=self.id)
            self.sio.emit(
                "tour", {"salon": self.__infos_salon(), "joueur": self.joueurs[self.manche.j].infos_publiques()}, room=self.id)

    def jouer_cartes(self, sid, cartes: list[int]):
        if self.manche is None:
            return {
                "status": 400,
                "message": "Impossible de jouer les cartes",
            }

        j = self.manche.j

        if sid != self.joueurs[j].sid:
            return {
                "status": 400,
                "message": "Ce n'est pas votre tour",
            }

        action = self.manche.jouer_cartes(cartes)
        if action["status"] == 200:
            # Mise à jour des joueurs
            self.joueurs[j] = self.manche.joueurs[j]

            # Joueur suivant
            # Skip les joueurs sans cartes
            while len(self.joueurs[self.manche.j].main) == 0:
                self.manche.j = (self.manche.j + 1) % 4

            self.sio.emit(
                "update_moi", self.joueurs[j].infos_privees(), to=sid)
            self.sio.emit(
                "tour", {"salon": self.__infos_salon(), "joueur": self.joueurs[self.manche.j].infos_publiques()}, room=self.id)
        elif action["status"] == 100:  # Fin de la manche
            # Assignation des rôles
            for i in range(4):
                self.joueurs[i].role = self.manche.roles_assignes[i]

            # Tri des joueurs (0: trouduc, 1: secrétaire, 2: vice-président, 3: président)
            joueurs_tries = [None for _ in range(4)]
            roles = ["🤡", "📝", "🥈", "👑"]

            for i in range(4):
                for j in range(4):
                    if self.joueurs[j].role == roles[i]:
                        joueurs_tries[i] = self.joueurs[j]
                        break

            self.joueurs = joueurs_tries

            # Fin de la manche
            self.manche = None
            self.sio.emit("update_salon", self.__infos_salon(), room=self.id)

            return {
                "status": 200,
                "message": "Fin de la manche",
            }

        return action

    def donner_cartes(self, sid, cartes: list[int]):
        if not self.attente_echanges:
            return {
                "status": 400,
                "message": "Impossible de donner les cartes",
            }

        # Trouver le joueur
        j = -1
        for i in range(4):
            if self.joueurs[i].sid == sid:
                j = i
                break

        if j == -1:
            return {
                "status": 400,
                "message": "Joueur non trouvé",
            }

        # Vérifier si le joueur est bien le président ou le vice-président
        if self.joueurs[j].role not in ["👑", "🥈"]:
            return {
                "status": 400,
                "message": "Vous n'avez pas le choix des cartes à donner",
            }

        # Vérifier si le joueur a donné le bon nombre de cartes
        if len(cartes) != (2 if self.joueurs[j].role == "👑" else 1):
            return {
                "status": 400,
                "message": "Vous devez donner le bon nombre de cartes",
            }

        # Vérifier si les cartes données sont bien dans la main du joueur
        for carte in cartes:
            if not 0 <= carte < len(self.joueurs[j].main):
                return {
                    "status": 400,
                    "message": "Une erreur est survenue",
                }

        # Vérifier si les cartes données sont bien différentes
        if len(cartes) != len(set(cartes)):
            return {
                "status": 400,
                "message": "Vous devez jouer 2 cartes différentes",
            }

        # Procéder à l'échange
        # Président
        main_president = self.joueurs[3].main
        for carte in cartes:
            del main_president[carte]
            self.joueurs[3].main = main_president
            self.joueurs[0].main.append(self.joueurs[3].main[carte])

        # Vice-président
        main_vice_president = self.joueurs[2].main
        for carte in cartes:
            del main_vice_president[carte]
            self.joueurs[2].main = main_vice_president
            self.joueurs[1].main.append(self.joueurs[2].main[carte])

        self.echanges_effectues += 1

        if self.echanges_effectues == 2:
            self.attente_echanges = False
            self.debut_manche()

        return {
            "status": 200,
            "message": "Cartes données",
        }

    def ajouter_joueur(self, nom, sid):
        if self.manche is not None:
            return {
                "status": 400,
                "message": "Impossible de rejoindre le salon",
            }

        # Le joueur est déjà dans le salon
        for joueur in self.joueurs:
            if joueur is None:
                continue

            if joueur.sid == sid:
                return {
                    "status": 200,
                    "message": "Salon rejoint",
                    "data": {
                        "salon": self.__infos_salon(),
                        "moi": joueur.infos_privees()
                    }
                }

            if joueur.nom == nom:
                return {
                    "status": 400,
                    "message": "Nom déjà utilisé",
                }

        # Le salon est plein
        if all(self.joueurs):
            return {
                "status": 400,
                "message": "Impossible de rejoindre le salon",
            }

        i = 0
        for _ in range(4):
            i += 1
            if self.joueurs[i] is None:
                self.joueurs[i] = Joueur(
                    sid,
                    nom,
                    main=self.cartes[(13 * i):(13 * (i + 1))],
                    role=""
                )
                break

        self.sio.emit("update_salon", self.__infos_salon(), room=self.id)

        return {
            "status": 200,
            "message": "Salon rejoint",
            "data": {
                "salon": self.__infos_salon(),
                "moi": self.joueurs[i].infos_privees()
            }
        }

    def retirer_joueur(self, nom=None, sid=None, expulsion=False):
        if self.manche is not None:
            return False

        for i in range(4):
            if self.joueurs[i] is None:
                continue
            if self.joueurs[i].nom == nom or self.joueurs[i].sid == sid:
                sid = self.joueurs[i].sid
                self.joueurs[i] = None
                break

        if expulsion:
            self.sio.emit("expulsion", to=sid)

        self.sio.leave_room(sid, self.id)
        self.sio.emit("update_salon", self.__infos_salon(), room=self.id)

        return True

    def __infos_salon(self):
        joueurs = []
        for joueur in self.joueurs:
            if joueur is not None:
                joueurs.append(joueur.infos_publiques())

        return {
            "id": self.id,
            "nom": self.nom,
            "manche": self.manche.infos() if self.manche is not None else None,
            "numero_manche": self.numero_manche,
            "joueurs": joueurs,
            "createur": self.createur,
            "attente": self.attente,
            "attente_echanges": self.attente_echanges,
        }

    def __gen_cartes(self):
        F = ["pique", "coeur", "carreau", "trefle"]
        H = ["J", "Q", "K", "A"]

        cartes = []

        i = 0
        for f in F:
            for j in range(1, 10):
                cartes.append((f, str(j + 1)))
                i += 1
            for h in H:
                cartes.append((f, h))
                i += 1

        return cartes

    def __shuffle(self, L):
        for _ in range(3):
            for i in range(len(L)):
                j = randint(0, len(L) - 1)
                L[i], L[j] = L[j], L[i]
        return L

    def __distribuer_cartes(self, jeu):
        def meilleures_cartes(jeu):
            H = ["J", "Q", "K", "A"]
            maxi = [0, 0]
            indice = [0, 0]

            for i in range(len(jeu)):
                try:
                    valeur = int(jeu[i][1])
                except ValueError:
                    valeur = H.index(jeu[i][1]) + 11

                if valeur == 2:
                    valeur = 15

                if valeur > maxi[0]:
                    maxi[1] = maxi[0]
                    indice[1] = indice[0]
                    maxi[0] = valeur
                    indice[0] = i
                elif valeur > maxi[1]:
                    maxi[1] = valeur
                    indice[1] = i

            return indice

        # Division du jeu en 4
        jeu = [jeu[13 * i: 13 * (i + 1)] for i in range(4)]

        # 2 meilleures cartes du trouduc -> président
        carte1_trouduc, carte2_trouduc = meilleures_cartes(jeu[0])
        jeu[3].append(jeu[0][carte1_trouduc])
        jeu[3].append(jeu[0][carte2_trouduc])

        if carte1_trouduc < carte2_trouduc:
            carte2_trouduc -= 1

        del jeu[0][carte1_trouduc]
        del jeu[0][carte2_trouduc]

        # Meilleure carte du secrétaire -> vice-président
        carte1_secretaire, _ = meilleures_cartes(jeu[1])
        jeu[2].append(jeu[1][carte1_secretaire])
        del jeu[1][carte1_secretaire]

        # jeu = choisir(2, 3, 0, jeu) # Choix des cartes (2) à donner par le président au trouduc
        # jeu = choisir(1, 2, 1, jeu) # Choix de la carte à donner par le vice-président au secrétaire

        return jeu, [[carte1_trouduc, carte2_trouduc], [carte1_secretaire]]
