<script lang="ts">
	import { Socket } from "socket.io-client";
	import type { Payload } from "src/types";
	import { link, replace } from "svelte-spa-router";

	export let socket: Socket;

	let eNomCreateur: HTMLInputElement;
	let eNom: HTMLInputElement;

	const newRoom = async (event: Event) => {
		event.preventDefault();

		const nom_createur = eNomCreateur.value;
		const nom = eNom.value;

		if (!nom_createur || !nom) {
			alert("Veuillez remplir tous les champs");
			return;
		}

		socket.emit(
			"nouveau_salon",
			{ nom_createur, nom },
			(payload: Payload) => {
				if (payload.status === 200) {
					localStorage.setItem("nom", nom_createur);
					replace("/salon/" + payload.data.id);
				} else {
					alert(payload.message);
				}
			}
		);
	};
</script>

<main class="flex flex-col items-center justify-center min-h-screen">
	<div class="bg-white p-12 rounded shadow-lg">
		<a class="text-gray-700 hover:text-gray-500" href="/" use:link>Retour</a
		>

		<h1 class="text-6xl font-bold">Le jeu du Trouduc</h1>

		<h2 class="text-2xl mt-8 underline">Créer une partie</h2>
		<form
			class="flex flex-col items-start justify-center space-y-4 mt-4"
			on:submit={newRoom}
		>
			<div class="flex flex-col w-full">
				<label for="nomCreateur" class="text-xl">Votre nom</label>
				<input
					bind:this={eNomCreateur}
					type="text"
					id="nomCreateur"
					placeholder="Jean Dupont"
					class="w-full p-2 border border-gray-300 rounded"
					value={localStorage.getItem("nom") || ""}
				/>
			</div>

			<div class="flex flex-col w-full">
				<label for="nom" class="text-xl">Nom de la partie</label>
				<input
					bind:this={eNom}
					type="text"
					id="nom"
					placeholder="Ma super partie"
					class="w-full p-2 border border-gray-300 rounded"
				/>
			</div>

			<button
				type="submit"
				class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
			>
				Créer la partie
			</button>
		</form>
	</div>
</main>
