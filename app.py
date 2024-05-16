import os
import random
import string
from logging.config import dictConfig

from flask import Flask, redirect, render_template, request
from flask_socketio import SocketIO, join_room, leave_room

from classes.salon import Salon

dictConfig({
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(module)s] [%(levelname)s]: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": "logs/app.log",
            "maxBytes": 1024,
            "backupCount": 3,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": "logs/error.log",
            "maxBytes": 1024,
            "backupCount": 3,
            "level": "ERROR",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file", "error_file"],
    },
})

app = Flask(
    __name__,
    static_folder=os.path.abspath("./client/dist"),
    template_folder=os.path.abspath("./client/dist"),
)
sio = SocketIO(app, cors_allowed_origins="*")

salons: dict[str, Salon] = dict()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<path:path>")
def catch_all(path):
    if os.path.exists(os.path.abspath(f"./client/dist/{path}")):
        return app.send_static_file(path)

    return redirect(f"/#/{path}")


@sio.event
def connect():
    app.logger.info("(sid %s) Connecté", request.sid)


@sio.event
def disconnect():
    app.logger.info("(sid %s) Déconnecté", request.sid)

    if not salons:
        return

    for salon in salons.values():
        if salon.retirer_joueur(sid=request.sid):
            leave_room(salon.id)
            break

    for salon in salons.values():
        if salon.createur == request.sid:
            del salons[salon.id]
            break


@sio.event
def nouveau_salon(data):
    app.logger.info("(sid %s) Nouveau salon", request.sid)
    app.logger.info(data)

    def gen_id():
        salon_id = "".join(random.choices(string.ascii_uppercase, k=6))

        if salon_id in salons:
            return gen_id()
        return salon_id

    salon_id = gen_id()
    salons[salon_id] = Salon(sio, salon_id, data["nom"],
                             data["nom_createur"], request.sid)

    join_room(salon_id)

    return {
        "status": 200,
        "message": "Salon créé",
        "data": {
            "id": salon_id,
            "nom": data["nom"],
            "nom_createur": data["nom_createur"],
        },
    }


@sio.event
def salon_existant(data):
    if data["id"] in salons:
        return {
            "status": 200,
            "message": "Salon existant"
        }

    return {
        "status": 400,
        "message": "Identifiant de partie invalide"
    }


@sio.event
def rejoindre(data):
    app.logger.info("(sid %s) Rejoindre salon", request.sid)
    app.logger.info(data)

    salon = salons.get(data["id_salon"])

    if not salon:
        return {
            "status": 404,
            "message": "Salon non trouvé",
        }

    join_room(data["id_salon"])

    return salon.ajouter_joueur(data["nom"], request.sid)


@sio.event
def expulser(data):
    app.logger.info("(sid %s) Expulser joueur", request.sid)
    app.logger.info(data)

    salon = salons.get(data["id_salon"])

    if not salon:
        return {
            "status": 404,
            "message": "Salon non trouvé",
        }

    return salon.retirer_joueur(data["nom"], expulsion=True)


@sio.event
def deconnexion(data):
    app.logger.info("(sid %s) Déconnexion", request.sid)
    app.logger.info(data)

    salon = salons.get(data["id_salon"])

    if not salon:
        return {
            "status": 404,
            "message": "Salon non trouvé",
        }

    return salon.retirer_joueur(sid=request.sid)


@sio.event
def debut_manche(data):
    app.logger.info("(sid %s) Début manche", request.sid)
    app.logger.info(data)

    salon = salons.get(data["id_salon"])

    if not salon:
        return {
            "status": 404,
            "message": "Salon non trouvé",
        }

    app.logger.info("%s, %s", salon.numero_manche, salon.echanges_effectues)
    salon.debut_manche()
    return True


@sio.event
def jouer_cartes(data):
    app.logger.info("(sid %s) Jouer cartes", request.sid)
    app.logger.info(data)

    salon = salons.get(data["id_salon"])

    if not salon:
        return {
            "status": 404,
            "message": "Salon non trouvé",
        }

    return salon.jouer_cartes(request.sid, data["cartes"])


@sio.event
def donner_cartes(data):
    app.logger.info("(sid %s) Donner cartes", request.sid)
    app.logger.info(data)

    salon = salons.get(data["id_salon"])

    if not salon:
        return {
            "status": 404,
            "message": "Salon non trouvé",
        }

    return salon.donner_cartes(request.sid, data["cartes"])


@sio.event
def cartes_a_jouer(data):
    app.logger.info("(sid %s) Cartes à jouer", request.sid)
    app.logger.info(data)

    salon = salons.get(data["id_salon"])

    if not salon:
        return {
            "status": 404,
            "message": "Salon non trouvé",
        }

    sio.emit("cartes_a_jouer", data["cartes"], room=salon.id)

    return True


if __name__ == "__main__":
    sio.run(app, host="0.0.0.0", port=8443,
            certfile="cert.pem", keyfile="key.pem")
