
<script setup>
import { ref } from 'vue';
import '../assets/styles/login.css';
import { apiRequest } from '../api';
// const emitted = defineEmits(['navigate']);

const loading = ref(false);
const emit = defineEmits(['navigate']);
const mode = ref('login'); // 'login' or 'register'
const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const role = ref('customer');
const error = ref('');

const toggleMode = () => {
	mode.value = mode.value === 'login' ? 'register' : 'login';
	error.value = '';
}

const handleLogin = async () => {
	error.value = '';
	loading.value = true;

	try {
		if (mode.value === 'register' && password.value !== confirmPassword.value) {
			throw new Error('Passwords do not match');
		}

		const endpoint = mode.value === 'login' ? '/api/auth/login' : '/api/auth/register';
		const body = mode.value === 'login'
			? { email: email.value, password: password.value }
			: {
				username: username.value,
				email: email.value,
				password: password.value,
				role: role.value
			};

		const data = await apiRequest(endpoint, {
			method: 'POST',
			body: JSON.stringify(body),
		});

		if (mode.value === 'register') {
			mode.value = 'login';
			alert('Registration successful! Please log in.');
			return;
		}

		localStorage.setItem('token', data.token);
		localStorage.setItem('user', JSON.stringify(data.user));
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
			<h2 class ="loginTitle">{{ mode === 'login' ? 'Login' : 'Register' }}</h2>

			<form @submit.prevent="handleLogin">
				<div v-if="mode === 'register'" class = "inputGroup">
					<label>Username</label>
					<input v-model="username" type="text" placeholder="Enter your username" required />
				</div>

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

				<div v-if="mode === 'register'" class="inputGroup">
					<label>Role</label>
					<select v-model="role">
						<option value="customer">Student</option>
						<option value="provider">Provider</option>
					</select>
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
