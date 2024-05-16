<script lang="ts">
	import Router from "svelte-spa-router";
	import { wrap } from "svelte-spa-router/wrap";
	import Accueil from "./routes/Accueil.svelte";
	import NouveauSalon from "./routes/NouveauSalon.svelte";

	import { io } from "socket.io-client";
	import RejoindreSalon from "./routes/RejoindreSalon.svelte";
	import Salon from "./routes/Salon.svelte";

	const socket = io(location.origin, {
		transports: ["websocket"],
	});

	socket.onAny((event, ...args) => {
		console.log(event, args);
	});
</script>

<img
	class="absolute -z-10 top-0 left-0 w-full h-screen object-cover opacity-50 filter blur-sm"
	src="/assets/img/background.jpg"
	alt="Background"
/>

<Router
	routes={{
		"/": Accueil,
		"/new": wrap({
			component: NouveauSalon,
			props: { socket },
		}),
		"/join": wrap({
			component: RejoindreSalon,
			props: { socket },
		}),
		"/salon/:id": wrap({
			component: Salon,
			props: { socket },
		}),
		"*": Accueil,
	}}
/>

<style lang="postcss">
	:global(body) {
		overflow-x: hidden;
	}
</style>
