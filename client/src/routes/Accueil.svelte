<script lang="ts">
	import { link } from "svelte-spa-router";
</script>

<main class="flex flex-col items-center justify-center min-h-screen">
	<div class="bg-white p-12 rounded shadow-lg max-w-2xl">
		<h1 class="text-6xl font-bold text-center">Le jeu du Trouduc</h1>

		<h2 class="text-2xl mt-2 text-center text-gray-700">
			Jouez au Trouduc en ligne avec vos amis&nbsp;!
		</h2>

		<p class="text-xl mt-4">
			Le jeu du Trouduc est un jeu de cartes qui se joue à 4. Le but est
			de se débarrasser de toutes ses cartes le plus rapidement possible.
			Le dernier joueur à avoir des cartes en main est le Trouduc.
		</p>

		<div class="flex flex-row items-center justify-center space-x-4 mt-8">
			<a
				href="/new"
				use:link
				class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
			>
				Créer une partie
			</a>
			<a
				href="/join"
				use:link
				class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
			>
				Rejoindre une partie
			</a>
		</div>
	</div>
</main>
