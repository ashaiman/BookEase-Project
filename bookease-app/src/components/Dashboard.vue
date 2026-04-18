<template>
	<div class="dashboard" v-if="user">
		<h2>Dashboard</h2>

		<p v-if="user.role === 'admin'">Admin Panel</p>
		<p v-else>Student Dashboard</p>


			<!-- Admin Buttons -->
			<div v-if="user && user.role === 'admin'">
			<p>Manage Services</p>
			<button @click="showCreate = true">Create Service</button>
			<button @click="showEdit = true">Edit Service</button>
			<button @click="showCancellations = true">View Cancellations</button>
		</div>

		
			<!-- Student Buttons -->
			 <div v-else>
			<p>View Your Bookings</p>
			<ul>
				<li
					v-for="student in upcoming" :key="student.id"> {{ student.name }} - {{ student.time }}
					<button @click="cancelBooking(student.id)">Cancel</button>
				</li>
			</ul>
		</div>
		<button @click="$emit('navigate', 'HomeView')">Back</button>

		<!-- Create Service Modal -->
		<div v-if="showCreate" class="modal">
			<h3>Create New Service</h3>

			<input v-model="newService.name" placeholder="Service Name" />
			<input v-model="newService.duration" placeholder="Duration (mins)" type="number" />

			<button @click="submitCreate" :disabled="loadingCreate">
				{{ loadingCreate ? 'Saving...' : 'Save' }}
			</button>
			<button @click="showCreate = false">Close</button>
		</div>


		<!-- Edit Service Modal -->
		<div v-if="showEdit" class="modal">
			<h3>Edit Service</h3>

			<p v-if="loadingServices">Loading services...</p>
			<ul v-else>
				<li v-for="service in services" :key="service.id">
					{{ service.name }} ({{ service.duration }} mins)
					<button @click="startEdit(service)">Edit</button>
				</li>
			</ul>

			<!-- Editing form -->
			<div v-if="editingService">
				<h4>Editing: {{ editingService.name }}</h4>
				<input v-model="editingService.name" placeholder="Service Name" />
				<input v-model="editingService.duration" placeholder="Duration (mins)" type="number" />
				<button @click="submitEdit">Save Changes</button>
				<!-- <button @click="editingService = null">Cancel</button> -->
			</div>
			
			<button @click="showEdit = false">Close</button>
		</div>

		<!-- View Cancellations Modal -->
		<div v-if="showCancellations" class="modal">
			<h3>View Cancellations</h3>

			<p v-if="loadingCancellations">Loading cancellations...</p>

			<p v-else-if="cancellations.length === 0">No cancellations to show.</p>

			<ul v-else>
				<li v-for="cancellation in cancellations" :key="cancellation.id">
					{{ cancellation.service }} - {{ cancellation.date }} (Cancelled by {{ cancellation.student }})
				</li>
			</ul>
			<button @click="showCancellations = false">Close</button>
		</div>

		<div v-else>
			<p>Please Log In to view dashboard.</p>
		</div>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import "../assets/styles/dashboard.css";

const props = defineProps({
	user: Object
});

// placeholder admin user
const testAdmin = {
	id: 999,
	name: "Admin User",
	email: "admin@example.com",
	role: "admin"
};

// Test admin user if no active user
const user = computed(() => props.user || testAdmin);

// Modal States
const showCreate = ref(false);
const showEdit = ref(false);
const showCancellations = ref(false);

// Loading States
const loadingCreate = ref(false);
const loadingServices = ref(false);
const loadingCancellations = ref(false);

// Form Modal
const newService = ref({
	name: '',
	duration: ''
});

// Data Lists
const services = ref([]);
const cancellations = ref([]);

const editingService = ref(null);

// Student Bookings Placeholder
const upcoming = ref([
	{ id: 1, name: "Math Tutoring", time: "10:00 AM" },
	{ id: 2, name: "Writing Center", time: "2:00 PM" }
]);

function cancelBooking(id) {
	// ASK API
	alert(`Booking with id ${id} cancelled!`);
	upcoming.value = upcoming.value.filter(student => student.id !== id);
}

// Create Service
async function submitCreate() {
	loadingCreate.value = true;
	
	// ASK API

	console.log("Creating service:", newService.value);

	services.value.push({
		id: Date.now(), // Placeholder ID
		name: newService.value.name,
		duration: Number(newService.value.duration)
	});

	loadingCreate.value = false;
	showCreate.value = false;
}

// Edit Service
async function openEdit() {
	showEdit.value = true;
	loadServices();
}

	async function loadServices() {
	loadingServices.value = true;

	// ASK API

	// Placeholder data
	services.value = [
		{ id: 1, name: "Math Tutoring", duration: 30 },
		{ id: 2, name: "Writing Center", duration: 45 }
	];

	loadingServices.value = false;
}

function startEdit(service) {
	editingService.value = { ...service };
}

function submitEdit() {
	// ASK API

	const index = services.value.findIndex(student => student.id === editingService.value.id);
	if (index !== -1) {
		services.value[index] = { ...editingService.value };
	}

	alert(`Service ${editingService.value.name} updated!`);
	editingService.value = null;
	// showEdit.value = false;
}


// Load Cancellations
function viewCancellations() {
	showCancellations.value = true;
	loadCancellations();
}

async function loadCancellations() {
	loadingCancellations.value = true;
	// loadCancellations();

	// ASK API

	// Placeholder data
	cancellations.value = [
		{ id: 1, service: "Math Tutoring", date: "2026-07-01 10:00", student: "John Doe" },
		{ id: 2, service: "Writing Center", date: "2026-07-02 14:00", student: "Jane Smith" }
	];

	loadingCancellations.value = false;
}

// const emit = defineEmits(['navigate']);

// const loadingCreate = ref(false);
// const loadingServices = ref(false);
// const loadingCancellations = ref(false);

// const upcoming = ref([
// 	{ id: 1, name: "Math Tutoring", time: "10:00 AM" },
// 	{ id: 2, name: "Writing Center", time: "2:00 PM" }
// ]); // Placeholder data

// function cancelBooking(id) {
// 	// Here you would send a request to your backend to cancel the booking
// 	// For now, we'll just remove it from the upcoming list
// 	alert(`Booking with id ${id} cancelled!`);
// 	upcoming.value = upcoming.value.filter(s => s.id !== id);
// }

// function createService() {
// 	//API call to create service
// }

// function editService() {
// 	//API call to edit service
// }

// function viewCancellations() {
// 	//API call to view cancellations
// }

</script>