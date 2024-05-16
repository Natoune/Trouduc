interface CommonPayload {
	status: number;
	message: string;
}

interface SuccessPayload extends CommonPayload {
	status: 200;
	data: any;
}

interface ErrorPayload extends CommonPayload {
	status: 400 | 401 | 403 | 404 | 500;
	error: string;
}

export type Payload = SuccessPayload | ErrorPayload;

/* Jeu */
export type Role = "" | "🤡" | "📝" | "🥈" | "👑";

export type Carte = [
	"trefle" | "carreau" | "pique" | "coeur",
	"2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "10" | "J" | "Q" | "K" | "A"
];

export interface Joueur {
	nom: string;
	role: Role;
	nb_cartes: number;
	createur: boolean;
}

export interface Moi extends Joueur {
	sid: string;
	main: Array<Carte>;
}

export interface Manche {
	nb_cartes: number;
	dernier_coup: Array<Carte>;
	premier_tour: boolean;
	suite: number;
}

export interface Salon {
	id: string;
	nom: string;
	manche: Manche | null;
	numero_manche: number;
	joueurs: Array<Joueur>;
	createur: string;
	attente: boolean;
	attente_echanges: boolean;
}
