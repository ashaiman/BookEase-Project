<template>
	<div class="CalendarView">

		<!-- Calendar -->
		<FullCalendar
			:options="calendarOptions"
		/>

		<!-- Edit Modal -->
		<div v-if="showEdit" class="modalOverlay">
			<div class="modalBox">
				<h3>Edit Service</h3>
				<form @submit.prevent="saveEdits">
					<div>
						<label>Title:</label>
						<input v-model="editForm.title" type="text" placeholder="Service name" />
					</div>
					<div>
						<label>Time:</label>
						<input v-model="editForm.time" type="time" />
					</div>
					<div class="modalActions">
						<button type="button" @click="showEdit = false">Cancel</button>
						<button type="submit">Save</button>
					</div>
				</form>
			</div>
		</div>

		<!-- Side Panel -->
		<div v-if="selectedEvent" class="eventPanel">
			<h3>{{ selectedEvent.title }}</h3>
			<p>Start: {{ selectedEvent.start }}</p>

			<!-- STUDENT -->
			 <div v-if="user?.role !== 'admin'">
				<button @click="bookService">Book Slot</button>
				<button @click="cancelBooking">Cancel Booking</button>
			</div>

			<!-- ADMIN -->
			<div v-else-if="user?.role === 'admin'">
				<button @click="editService">Edit Service</button>
				<button @click="deleteService">Delete Service</button>
			</div>

			<button class="closeButton" @click="selectedEvent = null">Close</button>
		</div>
	</div>
</template>

<script setup>
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { ref, computed } from 'vue';
import "../assets/styles/calendarView.css";

const props = defineProps({
	user: Object,
	events: {
		type: Array,
		default: () => []
	}
})

const selectedEvent = ref(null);

// Format events for calendar
const formattedEvents = computed(() => {
	return props.events.map(event => ({
		id: event.id,
		title: event.title,
		start: event.start,
		end: event.end,
		// color: event.held ? "#ffcc00" : "#3788d8"
	}))
});

// Events for calendar
// const calendarOptions = computed (() =>
// 	props.events.map(event => ({
// 		id: event.id,
// 		title: event.title,
// 		start: event.start,
// 		end: event.end,
// 		// color: event.held ? "#ffcc00" : "#3788d8"
// 	}))
// );

// Handle event click
function handleEventClick(info) {
	selectedEvent.value = {
		id: info.event.id,
		title: info.event.title,
		start: info.event.startStr,
	};
}

// Calendar options
const calendarOptions = computed(() => ({
	plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
	initialView: 'dayGridMonth',
	headerToolbar: {
		left: 'prev,next today',
		center: 'title',
		right: 'dayGridMonth,timeGridWeek,timeGridDay'
	},
	events: formattedEvents.value,
	eventClick: handleEventClick
}));

// Actions

async function bookService() {
	if (!selectedEvent.value) return;
	console.log('Booking slot', selectedEvent.value.id);
	// ASK API to book service
	alert(`Booked slot ${selectedEvent.value.id}`);
}

async function cancelBooking() {
	if (!selectedEvent.value) return;
	console.log('Cancelling booking for slot', selectedEvent.value.id);
	// ASK API to cancel booking
	alert(`Cancelled booking for slot ${selectedEvent.value.id}`);
}


// MODAL VARS
const showEdit = ref(false);
const editForm = ref({
	id: null,
	title: '',
	time: ''
});
async function editService() {
	if (!selectedEvent.value) return;
	console.log('Editing service', selectedEvent.value.id);
	// ASK API to edit service

	// MODAL HERE
	editForm.value = {
		id: selectedEvent.value.id,
		title: selectedEvent.value.title,
		time: selectedEvent.value.start
	};
	showEdit.value = true;

	// alert(`Editing service ${selectedEvent.value.id}`);
	// ASK API TO SAVE EDITS
}

async function saveEdits() {
	if (!editForm.value.id) return;
	console.log('Saving edits for service', editForm.value);
	// ASK API to save edits
	alert(`Saved edits for service ${editForm.value}`);
	showEdit.value = false;
}

async function deleteService() {
	if (!selectedEvent.value) return;
	console.log('Deleting service', selectedEvent.value.id);
	// ASK API to delete service
	alert(`Deleted service ${selectedEvent.value.id}`);
}


</script>
