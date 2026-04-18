
<template>
	<div class="homeView">
		<h2>BOOKEASE HOME</h2>

		<!-- Students view -->
		<div v-if="user?.role !== 'admin'">
			<h3>Your Past Sessions</h3>

			<p v-if="loading">Loading past sessions...</p>

			<ul v-else class="sessionList">
				<li v-for="session in pastSessions" :key="session.id" class="sessionItem">
					<div class="sessionInfo">
						<h3>{{ session.serviceName }}</h3>
						<p>{{ session.date }} {{ session.time }}</p>
					</div>

					<button @click="openReview(session)">
						Leave Review
					</button>
				</li>
			</ul>
		</div>

		<!-- Admin view -->
		<div v-else>
			<!-- Admin Homepage -->
			<p>Welcome, {{ user?.name }}!</p>
		</div>

		<!-- Review Modal -->
		<div v-if="showReview" class="modalOverlay">
			<div class="modalBox">
				<h3>Leave a Review for {{ reviewForm.serviceName }}</h3>
				<form @submit.prevent="submitReview">
					<div>
						<label>Rating:</label>
						<select v-model="reviewForm.rating">
							<option value="" disabled>Select rating</option>
							<option v-for="n in 5" :key="n" :value="n">{{ n }} Stars</option>
						</select>
					</div>
					<div>
						<label>Comments:</label>
						<textarea v-model="reviewForm.comments" placeholder="Write your review here..."></textarea>
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

import {ref, computed, onMounted} from 'vue';
import "../assets/styles/home.css";

const props = defineProps({
	user: Object
});

// PLACEHOLDER DATA
const pastSessions = ref([
	{ id: 1, serviceName: "Interview Practice", date: "2026-04-01", time: "10:00 AM" },
	{ id: 2, serviceName: "Resume Review", date: "2026-04-10", time: "2:00 PM" },
]);

// Review Modal State
const loading = ref(false);
const showReview = ref(false);

const reviewForm = ref({
	sessionId: null,
	serviceName: '',
	rating: '',
	comments: ''
});

// Loading cycle
onMounted(async () => {
	loading.value = true;
	// ASK API
	loading.value = false;
});


// Open review modal
function openReview(session) {
	reviewForm.value = {
		sessionId: session.id,
		serviceName: session.serviceName,
		rating: '',
		comments: ''
	};
	showReview.value = true;
}

async function submitReview() {
	console.log("Submitting review:", reviewForm.value);
	// ASK API to submit reviewForm.value

	alert(`Review submitted for session ${reviewForm.value.sessionId} with rating ${reviewForm.value.rating} and comments: ${reviewForm.value.comments}`);
	showReview.value = false;
}


</script>

<!-- <script>
import "../assets/styles/home.css";

export default {
	data() {
		return {
			categories: [
				{
					name: "Career Services",
					services: [
						{ id: 0, name: "Interview Practice", description: "Get ready for your next big interview with our comprehensive practice sessions." },
						{ id: 1, name: "Resume Review", description: "Enhance your resume with expert feedback and personalized suggestions." },
						{ id: 2, name: "Career Coaching", description: "Receive personalized career guidance to help you achieve your professional goals." },
					]
				},
				{
					name: "Academic Support",
					services: [
						{ id: 3, name: "Tutoring", description: "Get personalized tutoring in a variety of subjects to help you excel academically." },
						{ id: 4, name: "Study Groups", description: "Join or create study groups to collaborate and learn with your peers." },
						{ id: 5, name: "Writing Assistance", description: "Improve your writing skills with expert feedback and guidance on your essays and papers." },
					]
				}
			]	
		}
	}
}

</script> -->