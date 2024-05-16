class Joueur:
    def __init__(self, sid, nom, main, role, createur=False):
        self.sid = sid
        self.nom = nom
        self.main = main
        self.role = role
        self.createur = createur

    def infos_publiques(self):
        return {
            "nom": self.nom,
            "role": self.role,
            "nb_cartes": len(self.main),
            "createur": self.createur,
        }

    def infos_privees(self):
        return {
            "sid": self.sid,
            "nom": self.nom,
            "main": self.main,
            "role": self.role,
            "createur": self.createur,
        }
