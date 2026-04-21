<template>
	<div class="dashboard" v-if="user">
		<section class="dashboardHero">
			<div>
				<h2>Dashboard</h2>
				<p>{{ roleLabel }}</p>
			</div>
			<div class="heroMeta">
				<span class="idPill">User ID {{ user.id }}</span>
			</div>
		</section>
		<p v-if="message" class="statusBanner">{{ message }}</p>
		<p v-if="error" class="statusBanner errorBanner">{{ error }}</p>

		<div v-if="user.role === 'admin' || user.role === 'provider'">
			<div class="sectionHeader">
				<div>
					<h3>Services</h3>
					<p>Create, edit, and manage service offerings.</p>
				</div>
				<div class="actionRow">
					<button @click="showCreate = true">Create Service</button>
					<button class="secondaryButton" @click="loadServices">Refresh Services</button>
				</div>
			</div>

			<ul>
				<li v-for="service in services" :key="service.id">
					<div class="listCopy">
						<strong>{{ service.name }}</strong>
						<span>{{ service.category || 'no category' }} • {{ service.duration }} mins</span>
					</div>
					<div class="listActions">
						<button class="secondaryButton" @click="startEdit(service)">Edit</button>
						<button @click="deleteService(service.id)">Delete</button>
					</div>
				</li>
			</ul>
		</div>

		<div v-if="user.role === 'provider'">
			<div class="sectionHeader">
				<div>
					<h3>Provider Schedule</h3>
					<p>Set when students are allowed to book.</p>
				</div>
			</div>
			<div class="modal">
				<select v-model.number="scheduleForm.day_of_week">
					<option :value="0">Monday</option>
					<option :value="1">Tuesday</option>
					<option :value="2">Wednesday</option>
					<option :value="3">Thursday</option>
					<option :value="4">Friday</option>
					<option :value="5">Saturday</option>
					<option :value="6">Sunday</option>
				</select>
				<input v-model="scheduleForm.start_time" type="time" />
				<input v-model="scheduleForm.end_time" type="time" />
				<button @click="submitSchedule">Save Schedule</button>
			</div>
			<ul>
				<li v-for="slot in schedule" :key="slot.id">
					<div class="listCopy">
						<strong>{{ dayLabel(slot.day_of_week) }}</strong>
						<span>{{ slot.start_time }} - {{ slot.end_time }}</span>
					</div>
					<div class="listActions">
						<button @click="deleteSchedule(slot.id)">Delete</button>
					</div>
				</li>
			</ul>
		</div>

		<div>
			<div class="sectionHeader">
				<div>
					<h3>{{ user.role === 'provider' ? 'Incoming Bookings' : 'Your Upcoming Bookings' }}</h3>
					<p>{{ user.role === 'provider' ? 'See what students have booked with you.' : 'Manage the sessions you have coming up.' }}</p>
				</div>
				<button class="secondaryButton" @click="loadUpcoming">Refresh Bookings</button>
			</div>
			<p v-if="loadingBookings" class="emptyState">Loading bookings...</p>
			<p v-else-if="upcoming.length === 0" class="emptyState">No upcoming bookings.</p>
			<ul v-else>
				<li v-for="booking in upcoming" :key="booking.id">
					<div class="listCopy">
						<strong>Booking #{{ booking.id }}</strong>
						<span>Service #{{ booking.service_id }} • {{ formatDate(booking.start_time) }} • {{ booking.status }}</span>
					</div>
					<div class="listActions">
						<button @click="cancelBooking(booking.id)">Cancel</button>
					</div>
				</li>
			</ul>
		</div>

		<button @click="$emit('navigate', 'HomeView')">Back</button>

		<div v-if="showCreate" class="modal">
			<h3>Create New Service</h3>
			<input v-model="newService.name" placeholder="Service Name" />
			<input v-model="newService.description" placeholder="Description" />
			<input v-model="newService.category" placeholder="Category" />
			<select v-model.number="newService.duration">
				<option :value="15">15 minutes</option>
				<option :value="30">30 minutes</option>
				<option :value="60">60 minutes</option>
			</select>
			<button @click="submitCreate" :disabled="loadingCreate">
				{{ loadingCreate ? 'Saving...' : 'Save' }}
			</button>
			<button @click="showCreate = false">Close</button>
		</div>

		<div v-if="editingService" class="modal">
			<h3>Edit Service</h3>
			<input v-model="editingService.name" placeholder="Service Name" />
			<input v-model="editingService.description" placeholder="Description" />
			<input v-model="editingService.category" placeholder="Category" />
			<select v-model.number="editingService.duration">
				<option :value="15">15 minutes</option>
				<option :value="30">30 minutes</option>
				<option :value="60">60 minutes</option>
			</select>
			<button @click="submitEdit">Save Changes</button>
			<button @click="editingService = null">Close</button>
		</div>
	</div>

	<div v-else class="dashboard">
		<p>Please log in to view your dashboard.</p>
	</div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { apiRequest } from '../api';
import "../assets/styles/dashboard.css";

const props = defineProps({
	user: Object
});

const user = computed(() => props.user);
const roleLabel = computed(() => {
	if (user.value?.role === 'admin') return 'Admin Panel';
	if (user.value?.role === 'provider') return 'Provider Dashboard';
	return 'Student Dashboard';
});

const showCreate = ref(false);
const loadingCreate = ref(false);
const loadingBookings = ref(false);
const message = ref('');
const error = ref('');

const newService = ref({
	name: '',
	description: '',
	category: '',
	duration: 30
});

const scheduleForm = ref({
	day_of_week: 0,
	start_time: '09:00',
	end_time: '17:00',
	max_attendees: 1
});

const services = ref([]);
const schedule = ref([]);
const upcoming = ref([]);
const editingService = ref(null);

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

function dayLabel(day) {
	return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day] || `Day ${day}`;
}

async function loadServices() {
	try {
		services.value = await apiRequest('/api/services');
	} catch (err) {
		setError(err);
	}
}

async function loadSchedule() {
	if (user.value?.role !== 'provider') return;
	try {
		schedule.value = await apiRequest('/api/schedule');
	} catch (err) {
		setError(err);
	}
}

async function loadUpcoming() {
	if (!user.value) return;
	loadingBookings.value = true;
	try {
		upcoming.value = await apiRequest('/api/bookings/upcoming');
	} catch (err) {
		setError(err);
	} finally {
		loadingBookings.value = false;
	}
}

async function submitCreate() {
	loadingCreate.value = true;
	try {
		const service = await apiRequest('/api/services', {
			method: 'POST',
			body: JSON.stringify(newService.value)
		});
		services.value.push(service);
		newService.value = { name: '', description: '', category: '', duration: 30 };
		showCreate.value = false;
		setMessage('Service created.');
	} catch (err) {
		setError(err);
	} finally {
		loadingCreate.value = false;
	}
}

function startEdit(service) {
	editingService.value = { ...service };
}

async function submitEdit() {
	try {
		const updated = await apiRequest(`/api/services/${editingService.value.id}`, {
			method: 'PUT',
			body: JSON.stringify(editingService.value)
		});
		const index = services.value.findIndex(service => service.id === updated.id);
		if (index !== -1) services.value[index] = updated;
		editingService.value = null;
		setMessage('Service updated.');
	} catch (err) {
		setError(err);
	}
}

async function deleteService(serviceId) {
	try {
		await apiRequest(`/api/services/${serviceId}`, { method: 'DELETE' });
		services.value = services.value.filter(service => service.id !== serviceId);
		setMessage('Service deleted.');
	} catch (err) {
		setError(err);
	}
}

async function submitSchedule() {
	try {
		const slot = await apiRequest('/api/schedule', {
			method: 'POST',
			body: JSON.stringify(scheduleForm.value)
		});
		schedule.value.push(slot);
		setMessage('Schedule saved.');
	} catch (err) {
		setError(err);
	}
}

async function deleteSchedule(slotId) {
	try {
		await apiRequest(`/api/schedule/${slotId}`, { method: 'DELETE' });
		schedule.value = schedule.value.filter(slot => slot.id !== slotId);
		setMessage('Schedule deleted.');
	} catch (err) {
		setError(err);
	}
}

async function cancelBooking(id) {
	try {
		await apiRequest(`/api/bookings/${id}/cancel`, { method: 'PUT' });
		upcoming.value = upcoming.value.filter(booking => booking.id !== id);
		setMessage('Booking cancelled.');
	} catch (err) {
		setError(err);
	}
}

onMounted(() => {
	loadServices();
	loadSchedule();
	loadUpcoming();
});
</script>
