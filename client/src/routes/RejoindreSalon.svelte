<script lang="ts">
	import { Socket } from "socket.io-client";
	import type { Payload } from "src/types";
	import { link, replace } from "svelte-spa-router";

	export let socket: Socket;

	let eRoomId: HTMLInputElement;
	let eNom: HTMLInputElement;

	const joinRoom = async (event: Event) => {
		event.preventDefault();

		const nom = eNom.value;
		const roomId = eRoomId.value.toUpperCase();

		if (!nom || !roomId) {
			alert("Veuillez remplir tous les champs");
			return;
		}

		socket.emit("salon_existant", { id: roomId }, (payload: Payload) => {
			if (payload.status === 200) {
				localStorage.setItem("nom", nom);
				replace("/salon/" + roomId);
			} else {
				alert(payload.message);
			}
		});
	};
</script>

<main class="flex flex-col items-center justify-center min-h-screen">
	<div class="bg-white p-12 rounded shadow-lg">
		<a class="text-gray-700 hover:text-gray-500" href="/" use:link>Retour</a
		>

		<h1 class="text-6xl font-bold">Le jeu du Trouduc</h1>

		<h2 class="text-2xl mt-8 underline">Rejoindre une partie</h2>
		<form
			class="flex flex-col items-start justify-center space-y-4 mt-4"
			on:submit={joinRoom}
		>
			<div class="flex flex-col w-full">
				<label for="nom" class="text-xl">Votre nom</label>
				<input
					bind:this={eNom}
					type="text"
					id="nom"
					placeholder="Jean Dupont"
					class="w-full p-2 border border-gray-300 rounded"
					value={localStorage.getItem("nom") || ""}
				/>
			</div>

			<div class="flex flex-col w-full">
				<label for="nom" class="text-xl">Identifiant de la partie</label
				>
				<input
					bind:this={eRoomId}
					type="text"
					id="roomId"
					placeholder="AAAAAA"
					class="w-full p-2 border border-gray-300 rounded"
				/>
			</div>

			<button
				type="submit"
				class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
			>
				Rejoindre une partie
			</button>
		</form>
	</div>
</main>
