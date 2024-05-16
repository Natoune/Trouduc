<script lang="ts">
	import type { Socket } from "socket.io-client";
	import type { Moi, Salon } from "src/types";
	import { link } from "svelte-spa-router";

	export let socket: Socket;
	export let params: { id: string };
	export let salon: Salon;
	export let moi: Moi;

	function deconnexion() {
		socket.emit("deconnexion", { id_salon: params.id });
	}

	function debut_manche() {
		socket.emit("debut_manche", { id_salon: params.id });
	}
</script>

<a
	class="text-gray-700 hover:text-gray-500"
	href="/"
	on:click={deconnexion}
	use:link>Retour</a
>

<h1 class="text-6xl font-bold">{salon.nom}</h1>

<h2 class="text-2xl mt-8">
	En attente des autres joueurs pour démarrer la partie...
</h2>

<div class="flex flex-col items-center justify-center space-y-4 mt-4">
	<div class="flex flex-col w-full">
		Identifiant du salon&nbsp;:
		<span class="text-2xl font-bold">
			{salon.id}
		</span>
	</div>

	<div class="flex flex-col w-full">
		<label for="lien" class="text-xl">Lien de partage</label>
		<input
			type="text"
			id="lien"
			class="w-full p-2 border border-gray-300 rounded"
			value={location.origin + "/salon/" + salon.id}
			readonly
		/>
	</div>

	<hr class="border-t border-gray-300 w-full my-4" />

	<div class="flex flex-col w-full">
		<label for="joueurs" class="text-xl"
			>Joueurs ({salon.joueurs.length}/4)</label
		>
		<ul id="joueurs" class="w-full space-y-2">
			{#each salon.joueurs as joueur}
				<li
					class="flex items-center justify-between bg-gray-100 p-2 rounded"
				>
					<span>{joueur.nom}</span>
					{#if joueur.createur}
						<span class="text-sm font-bold text-yellow-500"
							>Créateur</span
						>
					{:else if moi.createur}
						<button
							type="button"
							class="text-sm text-red-500 border border-red-500 rounded px-2"
							on:click={() => {
								socket.emit("expulser", {
									id_salon: salon.id,
									nom: joueur.nom,
								});
							}}
						>
							Expulser
						</button>
					{/if}
				</li>
			{/each}
		</ul>
	</div>

	{#if moi.createur}
		<button
			type="button"
			class="w-full bg-blue-500 enabled:hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
			disabled={salon.joueurs.length < 4}
			on:click={debut_manche}
		>
			Lancer la partie
		</button>
	{/if}
</div>
