

<template>
	<nav class="MenuBar">
		<div class="left">
			<span class="logo" @click="emit('navigate', 'HomeView')">BookEase</span>
		</div>

		<div class="right">
			<button @click="emit('navigate', 'HomeView')">Home</button>
			<button @click="emit('navigate', 'Dashboard')">Dashboard</button>
			<button @click="emit('navigate', 'BookingCalendar')">Calendar</button>
			<button v-if="user" @click="emit('logout')">Logout ({{ user.username }})</button>
			<button v-else @click="emit('navigate', 'LoginForm')">Login</button>
		</div>
	</nav>
</template>

<script setup>
import "../assets/styles/menuBar.css";

const { user } = defineProps({
  user: Object
});

const emit = defineEmits(['navigate', 'logout']);

// export default {
// 	props: ["user"]
// }
</script>
