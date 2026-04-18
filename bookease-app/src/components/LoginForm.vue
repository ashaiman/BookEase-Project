
<script setup>
import { ref } from 'vue';
import '../assets/styles/login.css';
// const emitted = defineEmits(['navigate']);

const loading = ref(false);
const emit = defineEmits(['navigate']);
const mode = ref('login'); // 'login' or 'register'
const email = ref('');
const password = ref('');
const isLogin = ref(false);
const error = ref('');

const toggleMode = () => {
	mode.value = mode.value === 'login' ? 'register' : 'login';
	error.value = '';
}

const handleLogin = async () => {
	error.value = '';
	loading.value = true;

	try {

		const endpoint = mode.value === 'login' ? '/api/login' : '/api/register';

		const res = await fetch('/api/login', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ email: email.value, password: password.value }),
		});

		if (!res.ok) {
			throw new Error(`${mode.value} failed`);
		}

		const data = await res.json();
		localStorage.setItem('token', data.token);

		alert (`${mode.value} successful !`);
		emit('navigate', 'HomeView', { user: data.user });
	} catch (err) {
		error.value = err.message;
	} finally {
		loading.value = false;

	}
}

</script>

<template>

	<!-- Use loginContainer for css later -->
	<div class="loginContainer">
		<div class="loginCard">
			<h2 class ="loginTitle">Login</h2>
				{{ mode === 'login' ? 'Login' : 'Register' }}

			<form @submit.prevent="handleLogin">
				<div class = "inputGroup">
					<label>Email</label>
					<input v-model="email" type="email" placeholder="Enter your email" required />
				</div>
				
				<div class = "inputGroup">
					<label>Password</label>
					<input v-model="password" type="password" placeholder="Enter your password" required />
				</div>

				<!-- Register Text -->
				<div v-if="mode === 'register'" class="inputGroup">
					<label>Confirm Password</label>
					<input v-model="confirmPassword" type="password" placeholder="Confirm your password" required />
				</div>

				<button class="loginButton" :disabled="loading">
					{{ loading ? 'Processing...' : (mode === 'login' ? 'Login' : 'Register') }}

				</button>

				<p v-if="error" class="error">{{ error }}</p>
				
			</form>

			<p class="toggleText">
				{{ mode === 'login' ? "Don't have an account?" : "Already have an account?" }}
				<span @click="toggleMode" class="toggleLink">
					{{ mode === 'login' ? 'Register here' : 'Login here' }}
				</span> 
			</p>

			<!-- If page is on login mode, show login button, else show register button -->
			<!-- <h1>{{ isLogin ? "Login" : "Register" }}</h1> -->

			<!-- form submission -->
			<!-- <form @submit.prevent="isLogin ? login() : register()">
				<input type="text" placeholder="Username" v-model="username" required />
				<input type="password" placeholder="Password" v-model="password" required />
				<button type="submit">{{ isLogin ? "Login" : "Register" }}</button>
			</form> -->
		</div>

	<!-- <button @click="$emit('navigate', 'ServiceDetail', { service: ServiceCard.service })">Back</button> -->

	</div>

	
</template>


<!-- <script setup>

import { ref } from 'vue';

// default to login mode
const isLogin = ref(true);

</script> -->