<template>
	<div class="homeView">
		<h2>BookEase Home</h2>
		<p v-if="user">Welcome, {{ user.username }}.</p>
		<p v-else>Please log in to use BookEase.</p>
		<p v-if="message">{{ message }}</p>
		<p v-if="error" class="error">{{ error }}</p>

		<section>
			<h3>Services</h3>
			<div>
				<label>Filter by category</label>
				<input v-model="categoryFilter" placeholder="academic, career, wellbeing" />
				<button @click="loadServices">Search</button>
				<button @click="clearFilter">Clear</button>
			</div>

			<p v-if="loadingServices">Loading services...</p>
			<p v-else-if="services.length === 0">No services found.</p>
			<ul v-else class="sessionList">
				<li v-for="service in services" :key="service.id" class="sessionItem">
					<div class="sessionInfo">
						<h3>{{ service.name }}</h3>
						<p>{{ service.description || 'No description yet.' }}</p>
						<p>{{ service.category || 'uncategorized' }} - {{ service.duration }} minutes</p>
					</div>
					<button @click="$emit('navigate', 'BookingCalendar', { service })">
						Book
					</button>
				</li>
			</ul>
		</section>

		<section v-if="user">
			<h3>Your Past Sessions</h3>
			<button @click="loadHistory">Refresh History</button>

			<p v-if="loadingHistory">Loading past sessions...</p>
			<p v-else-if="pastSessions.length === 0">No past sessions yet.</p>
			<ul v-else class="sessionList">
				<li v-for="session in pastSessions" :key="session.id" class="sessionItem">
					<div class="sessionInfo">
						<h3>Booking #{{ session.id }}</h3>
						<p>Service #{{ session.service_id }}</p>
						<p>{{ formatDate(session.start_time) }}</p>
					</div>

					<button @click="openReview(session)">
						Leave Review
					</button>
				</li>
			</ul>
		</section>

		<div v-if="showReview" class="modalOverlay">
			<div class="modalBox">
				<h3>Leave a Review for Booking #{{ reviewForm.booking_id }}</h3>
				<form @submit.prevent="submitReview">
					<div>
						<label>Rating:</label>
						<select v-model.number="reviewForm.rating" required>
							<option value="" disabled>Select rating</option>
							<option v-for="n in 5" :key="n" :value="n">{{ n }} Stars</option>
						</select>
					</div>
					<div>
						<label>Comments:</label>
						<textarea v-model="reviewForm.comment" placeholder="Write your review here..."></textarea>
					</div>
					<div class="modalActions">
						<button type="button" @click="showReview = false">Cancel</button>
						<button type="submit">Submit Review</button>
					</div>
				</form>
			</div>
		</div>
	</div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { apiRequest } from '../api';
import "../assets/styles/home.css";

const props = defineProps({
	user: Object
});

defineEmits(['navigate']);

const services = ref([]);
const pastSessions = ref([]);
const loadingServices = ref(false);
const loadingHistory = ref(false);
const showReview = ref(false);
const message = ref('');
const error = ref('');
const categoryFilter = ref('');

const reviewForm = ref({
	booking_id: null,
	service_id: null,
	rating: '',
	comment: ''
});

function setMessage(text) {
	message.value = text;
	error.value = '';
}

function setError(err) {
	error.value = err.message || String(err);
	message.value = '';
}

function formatDate(value) {
	return new Date(value).toLocaleString();
}

async function loadServices() {
	loadingServices.value = true;
	try {
		const query = categoryFilter.value ? `?category=${encodeURIComponent(categoryFilter.value)}` : '';
		services.value = await apiRequest(`/api/services${query}`);
	} catch (err) {
		setError(err);
	} finally {
		loadingServices.value = false;
	}
}

function clearFilter() {
	categoryFilter.value = '';
	loadServices();
}

async function loadHistory() {
	if (!props.user) return;
	loadingHistory.value = true;
	try {
		pastSessions.value = await apiRequest('/api/bookings/history');
	} catch (err) {
		setError(err);
	} finally {
		loadingHistory.value = false;
	}
}

function openReview(session) {
	reviewForm.value = {
		booking_id: session.id,
		service_id: session.service_id,
		rating: '',
		comment: ''
	};
	showReview.value = true;
}

async function submitReview() {
	try {
		await apiRequest('/api/feedback', {
			method: 'POST',
			body: JSON.stringify(reviewForm.value)
		});
		showReview.value = false;
		setMessage('Review submitted.');
	} catch (err) {
		setError(err);
	}
}

onMounted(() => {
	loadServices();
	loadHistory();
});
</script>
