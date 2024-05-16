<script lang="ts">
	import type { Socket } from "socket.io-client";
	import type { Carte, Joueur, Moi, Payload, Salon } from "src/types";

	export let socket: Socket;
	export let salon: Salon;
	export let moi: Moi;

	export let set_salon: (s: Salon) => void;

	let tour: Joueur;
	let cartes_a_jouer: number[] = [];

	socket.on(
		"tour",
		({ salon: s, joueur }: { salon: Salon; joueur: Joueur }) => {
			set_salon(s);

			tour = joueur;

			for (const joueur of salon.joueurs) {
				update_cartes_a_jouer([], joueur.nom);
			}
		}
	);

	socket.on("cartes_a_jouer", (cartes: number[]) => {
		if (tour.nom === moi.nom) return;
		update_cartes_a_jouer(cartes, tour.nom);
	});

	function update_cartes_a_jouer(cartes: number[], joueur: string) {
		for (
			let i = 0;
			i < salon.joueurs.find((j) => j.nom === joueur)!.nb_cartes;
			i++
		) {
			let carte = document.querySelector(
				`img[id="${joueur}-${i}"]`
			) as HTMLImageElement;
			if (carte) {
				if (cartes.includes(i))
					carte.style.transform = "translateY(-12px) scale(1.1)";
				else carte.style.transform = "translateY(0) scale(1)";
			}
		}
	}

	function jouer_cartes() {
		socket.emit(
			"jouer_cartes",
			{
				id_salon: salon.id,
				cartes: cartes_a_jouer,
			},
			(payload: Payload) => {
				if (payload.status === 200) {
					for (const i of cartes_a_jouer) {
						let carte = document.querySelector(
							`img[data-index="${i}"]`
						) as HTMLImageElement;
						if (carte) {
							carte.style.position = "static";
							carte.style.zIndex = "auto";
							carte.style.left = "auto";
							carte.style.top = "auto";
						}
					}
					cartes_a_jouer = [];
				} else {
					alert(payload.message);
				}
			}
		);
	}

	function start_drag(event: MouseEvent) {
		event.preventDefault();
		if (!(tour.nom === moi.nom) || !event.target) return;

		let target = event.target as HTMLImageElement;
		target.style.position = "absolute";
		target.style.left = event.pageX - target.offsetWidth / 2 + "px";
		target.style.top = event.pageY - target.offsetHeight / 2 + "px";
		target.style.zIndex = "1000";

		return false;
	}

	function drag_carte(event: MouseEvent) {
		if (!(tour.nom === moi.nom) || !event.target) return;

		let target = event.target as HTMLImageElement;
		if (target.style.position !== "absolute") return;
		target.style.left = event.pageX - target.offsetWidth / 2 + "px";
		target.style.top = event.pageY - target.offsetHeight / 2 + "px";
		target.style.zIndex = "1000";

		if (cartes_a_jouer.includes(parseInt(target.dataset.index!))) {
			cartes_a_jouer = cartes_a_jouer.filter(
				(i) => i !== parseInt(target.dataset.index!)
			);
			socket.emit("cartes_a_jouer", {
				id_salon: salon.id,
				cartes: cartes_a_jouer,
			});
		}
	}

	function end_drag(event: MouseEvent) {
		if (!(tour.nom === moi.nom) || !event.target) return;
		let target = event.target as HTMLImageElement;

		if (
			event.pageX > window.innerWidth / 2 - 200 &&
			event.pageX < window.innerWidth / 2 + 200 &&
			event.pageY > window.innerHeight / 2 - 100 &&
			event.pageY < window.innerHeight / 2 + 100
		) {
			cartes_a_jouer = [
				...cartes_a_jouer,
				parseInt(target.dataset.index!),
			];
			socket.emit("cartes_a_jouer", {
				id_salon: salon.id,
				cartes: cartes_a_jouer,
			});

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

	// DEBUG
	let debug = false; window.addEventListener("keydown", (event) => { if (event.key === "d") debug = !debug; });
</script>

<svelte:head>
	<title>{tour && tour.nom === moi.nom ? "À vous de jouer !" : salon.nom}</title>
</svelte:head>

<img
	class="absolute top-0 left-0 w-full h-screen object-cover"
	src="/assets/img/tapis.jpg"
	alt="Tapis de jeu"
/>

{#if tour}
	<!-- DEBUG -->
	{#if debug && process.env.NODE_ENV === "development"}
		<div class="absolute top-0 left-0 p-4 z-50 max-h-screen text-white text-sm bg-yellow-500/50 overflow-auto flex flex-col items-start justify-start">
			<h2 class="text-xl font-bold">🐛 Informations de débogage</h2>
			<hr class="w-full border border-white/50 my-2" />
			<div class="flex items-start justify-start">
				<div class="border-r border-white/50 pr-4">
					<h2 class="text-xl font-bold">🛋️ Salon</h2>
					<pre>{JSON.stringify(salon, null, 2)}</pre>
				</div>

				<div class="pl-4">
					<h2 class="text-xl font-bold">👤 Moi</h2>
					<pre>{JSON.stringify(moi, null, 2)}</pre>
				</div>
			</div>
		</div>
	{/if}

	<!-- Bandeau d'infos -->
	<div
		class="absolute top-2 left-1/2 -translate-x-1/2 w-1/2 z-20 p-4 rounded-md bg-black/90 text-white flex items-center justify-between"
	>
		{#if tour.nom === moi.nom}
			<div class="flex flex-col items-start justify-start w-1/2">
				<h2 class="text-xl font-bold">À vous de jouer !</h2>
				{#if salon.manche!.suite > 0}
					<p class="text-sm text-red-500">
						⚠ Suite de cartes ! Vous devez jouer des cartes de même
						valeur que précédemment ou passer votre tour.
					</p>
				{/if}
			</div>

			{#if (salon.manche!.premier_tour && cartes_a_jouer.length > 0 && cartes_a_jouer.length <= 4) || (!salon.manche!.premier_tour && cartes_a_jouer.length == salon.manche!.nb_cartes)}
				<button
					type="button"
					class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
					on:click={jouer_cartes}
				>
					Jouer
				</button>
			{:else if !salon.manche!.premier_tour}
				<button
					type="button"
					class="bg-transparent border border-red-500 hover:bg-red-500 text-red-500 hover:text-white font-bold py-2 px-4 rounded transition-colors cursor-pointer"
					on:click={() => {
						cartes_a_jouer = [-1];
						jouer_cartes();
					}}
				>
					Passer mon tour
				</button>
			{/if}
		{:else}
			<h2 class="text-xl">
				Au tour de <span class="font-bold text-yellow-500">{tour.nom}</span>
				!
			</h2>
		{/if}
	</div>

	<!-- Défausse -->
	<div
		class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 flex justify-center"
	>
		{#each salon.manche!.dernier_coup as carte, i}
			<img
				class="h-32 -mr-8 -ml-8 transform transition-transform duration-300"
				style={`transform: translateX(${i * 8}px);`}
				src={`/assets/img/cards/${gifCarte(carte)}`}
				alt={`${carte[1]} de ${carte[0]}`}
			/>
		{/each}
	</div>

	<!-- Moi -->
	<div
		class="absolute bottom-0 left-0 w-full h-screen overflow-hidden z-10 flex items-end justify-center p-4 transform transition-transform duration-300"
		class:translate-y-10={!(tour.nom === moi.nom)}
	>
		{#each moi.main as carte}
			<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
			<img
				data-index={moi.main.indexOf(carte)}
				class="h-36 -mr-5 -ml-5 shadow-xl transform transition-transform duration-300"
				class:hover:scale-110={!cartes_a_jouer.includes(
					moi.main.indexOf(carte)
				) && tour.nom === moi.nom}
				class:hover:-translate-y-8={!cartes_a_jouer.includes(
					moi.main.indexOf(carte)
				) && tour.nom === moi.nom}
				src={`/assets/img/cards/${gifCarte(carte)}`}
				alt={`${carte[1]} de ${carte[0]}`}
				on:mousedown={start_drag}
				on:mousemove={drag_carte}
				on:mouseup={end_drag}
			/>
		{/each}
	</div>

	<!-- Joueur 2 -->
	<div
		class="absolute top-1/3 -translate-x-1/2 -translate-y-1/3 left-8 w-32 flex justify-start rotate-90"
	>
		{#each salon.joueurs as joueur, i}
			{#if i % 4 === 1}
				{#each Array.from({ length: joueur.nb_cartes }) as _, i}
					<img
						id={`${joueur.nom}-${i}`}
						class="h-32 -mr-8 -ml-8 transform transition-transform duration-300"
						src="/assets/img/card_back.png"
						alt="Dos de carte"
					/>
				{/each}
			{/if}
		{/each}
	</div>

	<!-- Player 3 -->
	<div
		class="absolute top-8 left-1/2 -translate-x-1/2 -translate-y-1/2 w-fit flex justify-start rotate-180"
	>
		{#each salon.joueurs as joueur, i}
			{#if i % 4 === 2}
				{#each Array.from({ length: joueur.nb_cartes }) as _, i}
					<img
						id={`${joueur.nom}-${i}`}
						class="h-32 -mr-8 -ml-8 transform transition-transform duration-300"
						src="/assets/img/card_back.png"
						alt="Dos de carte"
					/>
				{/each}
			{/if}
		{/each}
	</div>

	<!-- Player 4 -->
	<div
		class="absolute top-2/3 translate-x-1/2 -translate-y-2/3 right-8 w-32 flex justify-start -rotate-90"
	>
		{#each salon.joueurs as joueur, i}
			{#if i % 4 === 3}
				{#each Array.from({ length: joueur.nb_cartes }) as _, i}
					<img
						id={`${joueur.nom}-${i}`}
						class="h-32 -mr-8 -ml-8 transform transition-transform duration-300"
						src="/assets/img/card_back.png"
						alt="Dos de carte"
					/>
				{/each}
			{/if}
		{/each}
	</div>
{/if}
