<script lang="ts">
	import type { Socket } from "socket.io-client";
	import type { Moi, Salon } from "src/types";

	export let socket: Socket;
	export let salon: Salon;
	export let moi: Moi;

	let roles = {
		"": "",
		"👑": "Président",
		"🥈": "Vice-président",
		"📝": "Secrétaire",
		"🤡": "Trouduc",
	};

	let delay = 1;
	setTimeout(() => {
		document.querySelectorAll("#entry").forEach((joueur) => {
			setTimeout(() => {
				joueur.classList.add("appear");
			}, delay * 1000);
			delay += 0.5;
		});
	}, 500);

	let nextButton: HTMLButtonElement;
	if (moi.createur)
		setTimeout(() => nextButton.classList.add("appear"), 5000);

	function next() {
		socket.emit("debut_manche", { id_salon: salon.id });
	}
</script>

<h1 class="text-6xl font-bold">{salon.nom}</h1>

<h2 class="text-2xl mt-8">
	La manche n°{salon.numero_manche} est terminée&nbsp;!
</h2>

<div class="flex flex-col items-end justify-center mt-4">
	<div class="flex flex-col w-full space-y-4">
		{#each salon.joueurs.reverse() as joueur}
			<div id="entry" class="flex flex-col w-full opacity-0">
				<div class="flex items-center justify-between">
					<h3 class="text-2xl font-bold">
						{joueur.role}&nbsp;{joueur.nom}
					</h3>
					<p>{roles[joueur.role]}</p>
				</div>
			</div>
		{/each}
	</div>

	{#if moi.createur}
		<button
			bind:this={nextButton}
			class="bg-blue-500 text-white font-bold py-2 px-4 mt-8 rounded pointer-events-none opacity-0 transition-opacity cursor-pointer"
			on:click={next}
		>
			Manche suivante →
		</button>
	{/if}
</div>

<style lang="postcss">
	:global(.appear) {
		animation: appear 0.5s ease-in-out;
		animation-fill-mode: forwards;
	}

	@keyframes appear {
		0% {
			opacity: 0;
			transform: translateY(20px);
		}
		100% {
			opacity: 1;
			transform: translateY(0);
			pointer-events: all;
		}
	}
</style>
