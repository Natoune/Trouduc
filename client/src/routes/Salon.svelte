<script lang="ts">
	import type { Socket } from "socket.io-client";
	import { onMount } from "svelte";
	import { replace } from "svelte-spa-router";
	import AttenteEchanges from "../components/AttenteEchanges.svelte";
	import AttenteSalon from "../components/AttenteSalon.svelte";
	import FinManche from "../components/FinManche.svelte";
	import Manche from "../components/Manche.svelte";
	import type { Moi, Payload, Salon } from "../types";

	export let params: { id: string };
	export let socket: Socket;

	let salon: Salon;
	let moi: Moi;

	let chargement = true;

	onMount(() => {
		if (!localStorage.getItem("nom")) {
			const nom = prompt("Quel est votre nom ?");
			if (!!nom) {
				localStorage.setItem("nom", nom);
			} else {
				replace("/");
			}
		}

		socket.emit(
			"rejoindre",
			{ nom: localStorage.getItem("nom"), id_salon: params.id },
			(payload: Payload) => {
				if (payload.status === 200) {
					set_salon(payload.data.salon);
					set_moi(payload.data.moi);
					chargement = false;
				} else {
					alert(payload.message);
					replace("/");
				}
			}
		);
	});

	socket.on("update_moi", set_moi);
	socket.on("update_salon", set_salon);

	socket.on("expulsion", () => {
		alert("Vous avez été expulsé de la partie");
		replace("/");
	});

	function set_salon(s: Salon) {
		salon = {
			...s,
			joueurs: s.manche
				? s.joueurs.sort((a, b) => {
						if (
							a.nom ===
							(moi ? moi.nom : localStorage.getItem("nom"))
						)
							return -1;
						if (
							b.nom ===
							(moi ? moi.nom : localStorage.getItem("nom"))
						)
							return 1;
						return 0;
					})
				: s.joueurs,
		};
	}

	function set_moi(m: Moi) {
		moi = m;
	}
</script>

<svelte:head>
	<title>{salon ? salon.nom : "Chargement..."}</title>
</svelte:head>

<main class="flex flex-col items-center justify-center min-h-screen">
	<div class="bg-white p-12 rounded shadow-lg">
		{#if chargement}
			<svg
				width="24"
				height="24"
				viewBox="0 0 24 24"
				xmlns="http://www.w3.org/2000/svg"
				class="animate-spin"
				><path
					d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z"
					class="spinner_P7sC"
				/></svg
			>
		{:else if salon.attente}
			<AttenteSalon {socket} {params} {salon} {moi} />
		{:else if salon.attente_echanges}
			<AttenteEchanges {socket} {salon} />
		{:else if salon.manche}
			<Manche {socket} {salon} {moi} {set_salon} />
		{:else}
			<FinManche {socket} {salon} {moi} />
		{/if}
	</div>
</main>
