<script lang="ts">
	import type { Socket } from "socket.io-client";
	import type { Carte, Payload, Salon } from "src/types";

	export let socket: Socket;
	export let salon: Salon;

	let don_force = true;
	let donne = false;
	let main: Carte[] = [];
	let nb = 0;
	let cartes_a_donner: number[] = [];

	socket.on(
		"donner_cartes",
		(opts: { main: Carte[]; dons: number[]; nb: number }) => {
			main = opts.main;
			don_force = !!opts.dons;
			nb = opts.nb;

			if (opts.dons)
				setTimeout(() => {
					for (const i of opts.dons) {
						let carte = document.querySelector(
							`img[data-index="${i}"]`
						) as HTMLImageElement;
						if (carte) {
							carte.style.transform =
								"translateY(-50px) scale(1.1)";
						}
					}
				}, 1000);
		}
	);

	function donner_cartes() {
		donne = true;
		socket.emit(
			"donner_cartes",
			{
				id_salon: salon.id,
				cartes: cartes_a_donner,
			},
			(payload: Payload) => {
				if (payload.status === 200) {
					donne = true;
					for (const i of cartes_a_donner) {
						let carte = document.querySelector(
							`img[data-index="${i}"]`
						) as HTMLImageElement;
						if (carte) carte.remove();
					}
					cartes_a_donner = [];
				} else {
					donne = false;
					alert(payload.message);
				}
			}
		);
	}

	function start_drag(event: MouseEvent) {
		event.preventDefault();
		if (donne || don_force || !event.target) return;

		let target = event.target as HTMLImageElement;
		target.style.position = "absolute";
		target.style.left = event.pageX - target.offsetWidth / 2 + "px";
		target.style.top = event.pageY - target.offsetHeight / 2 + "px";
		target.style.zIndex = "1000";

		return false;
	}

	function drag_carte(event: MouseEvent) {
		if (donne || don_force || !event.target) return;

		let target = event.target as HTMLImageElement;
		if (target.style.position !== "absolute") return;
		target.style.left = event.pageX - target.offsetWidth / 2 + "px";
		target.style.top = event.pageY - target.offsetHeight / 2 + "px";
		target.style.zIndex = "1000";

		if (cartes_a_donner.includes(parseInt(target.dataset.index!))) {
			cartes_a_donner = cartes_a_donner.filter(
				(i) => i !== parseInt(target.dataset.index!)
			);
		}
	}

	function end_drag(event: MouseEvent) {
		if (donne || don_force || !event.target) return;
		let target = event.target as HTMLImageElement;

		if (
			event.pageX > window.innerWidth / 2 - 200 &&
			event.pageX < window.innerWidth / 2 + 200 &&
			event.pageY > window.innerHeight / 2 - 100 &&
			event.pageY < window.innerHeight / 2 + 100
		) {
			cartes_a_donner = [
				...cartes_a_donner,
				parseInt(target.dataset.index!),
			];

			target.style.position = "fixed";
			target.style.left = event.pageX - target.offsetWidth / 2 + "px";
			target.style.top = event.pageY - target.offsetHeight / 2 + "px";
			target.style.zIndex = "auto";
		} else {
			target.style.position = "static";
			target.style.left = "auto";
			target.style.top = "auto";
			target.style.zIndex = "auto";
		}
	}

	function gifCarte(carte: Carte) {
		const names = {
			pique: "spades",
			coeur: "hearts",
			carreau: "diamonds",
			trefle: "clubs",
			J: "jack",
			Q: "queen",
			K: "king",
			A: "ace",
		};

		let valeur = "";

		if (carte[1] in names) {
			valeur += names[carte[1] as keyof typeof names];
		} else {
			valeur += carte[1];
		}

		return valeur + "_of_" + names[carte[0]] + ".gif";
	}
</script>

<svelte:head>
	<title>{salon ? salon.nom : "Chargement..."}</title>
</svelte:head>

<img
	class="absolute top-0 left-0 w-full h-screen object-cover"
	src="/assets/img/tapis.jpg"
	alt="Tapis de jeu"
/>

<!-- Bandeau d'infos -->
<div
	class="absolute top-2 left-1/2 -translate-x-1/2 w-1/2 z-20 p-4 rounded-md bg-black/90 text-white flex items-center justify-between"
>
	{#if donne}
		<p>En attente des autres joueurs...</p>
	{:else if don_force}
		{#if nb === 2}
			<p>Vos 2 meilleures cartes vont être données au Président.</p>
		{:else}
			<p>Votre meilleure carte va être donnée au Vice-Président.</p>
		{/if}
	{:else if nb === 2}
		<p>Choisissez 2 cartes à donner au Trouduc.</p>
	{:else}
		<p>Choisissez 1 carte à donner au Secrétaire.</p>
	{/if}

	{#if !donne && !don_force && cartes_a_donner.length === nb}
		<button
			class="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-md"
			on:click={donner_cartes}
		>
			Donner
		</button>
	{/if}
</div>

<!-- Moi -->
<div
	class="absolute bottom-0 left-0 w-full h-screen overflow-hidden z-10 flex items-end justify-center p-4 transform transition-transform duration-300"
>
	{#each main as carte}
		<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
		<img
			data-index={main.indexOf(carte)}
			class="h-36 -mr-5 -ml-5 shadow-xl transform transition-transform duration-300"
			class:hover:scale-110={!cartes_a_donner.includes(
				main.indexOf(carte)
			) &&
				!don_force &&
				!donne}
			class:hover:-translate-y-8={!cartes_a_donner.includes(
				main.indexOf(carte)
			) &&
				!don_force &&
				!donne}
			class:duration-1000={don_force}
			class:ease-in-out={don_force}
			src={`/assets/img/cards/${gifCarte(carte)}`}
			alt={`${carte[1]} de ${carte[0]}`}
			on:mousedown={start_drag}
			on:mousemove={drag_carte}
			on:mouseup={end_drag}
		/>
	{/each}
</div>
