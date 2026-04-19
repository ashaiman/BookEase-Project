<template>
	<div class="BookingCalendar">
		<h1 v-if="service">Book: {{ service.name }}</h1>
		<p v-else>Select a service from Home first.</p>
		<p v-if="message">{{ message }}</p>
		<p v-if="error" class="error">{{ error }}</p>

		<div v-if="service" class="bookingControls">
			<label>
				Provider ID
				<input v-model.number="providerId" type="number" placeholder="Provider user ID" />
			</label>
			<label>
				Start date
				<input v-model="startDate" type="date" />
			</label>
			<label>
				End date
				<input v-model="endDate" type="date" />
			</label>
			<button @click="loadAvailability">Load Availability</button>
		</div>

		<FullCalendar :options="calendarOptions" />

		<TimerHoldBanner
			v-if="reservation?.reserved_until"
			:timeLeft="reservationSecondsLeft"
		/>

		<div v-if="selectedSlot" class="selectedSlot">
			<p>Selected schedule window: {{ selectedSlot.date }} {{ selectedSlot.start_time }}-{{ selectedSlot.end_time }}</p>
			<label>
				Appointment start time
				<input v-model="selectedStartTime" type="datetime-local" />
			</label>
			<button @click="reserveSlot">Reserve 15-Minute Hold</button>
			<button @click="bookSlot">Book Immediately</button>
		</div>

		<div v-if="reservation">
			<p>Reserved booking #{{ reservation.id }} until {{ formatDate(reservation.reserved_until) }}</p>
			<button @click="confirmReservation">Confirm Reservation</button>
		</div>
	</div>
</template>

<script setup>
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { computed, ref } from 'vue';
import { apiRequest } from '../api';
import TimerHoldBanner from '../components/TimerHoldBanner.vue';

const props = defineProps({
	selectedService: Object,
	user: Object
});

const service = computed(() => props.selectedService);
const providerId = ref('');
const startDate = ref(new Date().toISOString().slice(0, 10));
const endDate = ref(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10));
const availability = ref([]);
const bookedSlots = ref([]);
const selectedSlot = ref(null);
const selectedStartTime = ref('');
const reservation = ref(null);
const message = ref('');
const error = ref('');

const reservationSecondsLeft = computed(() => {
	if (!reservation.value?.reserved_until) return 0;
	return Math.max(0, Math.floor((parseUtcDate(reservation.value.reserved_until) - Date.now()) / 1000));
});

const calendarEvents = computed(() => {
	const availableEvents = availability.value.map((slot, index) => ({
		id: `available-${index}`,
		title: `Available ${slot.start_time}-${slot.end_time}`,
		start: `${slot.date}T${slot.start_time}:00`,
		end: `${slot.date}T${slot.end_time}:00`,
		color: '#2f855a',
		extendedProps: {
			type: 'available',
			slot
		}
	}));

	const bookedEvents = bookedSlots.value.map(slot => ({
		id: `booked-${slot.id}`,
		title: `${slot.status} booking`,
		start: slot.start_time,
		end: slot.end_time,
		color: '#c53030',
		extendedProps: {
			type: 'booked',
			slot
		}
	}));

	return [...availableEvents, ...bookedEvents];
});

const calendarOptions = computed(() => ({
	plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
	initialView: 'timeGridWeek',
	headerToolbar: {
		left: 'prev,next today',
		center: 'title',
		right: 'dayGridMonth,timeGridWeek,timeGridDay'
	},
	events: calendarEvents.value,
	eventClick(info) {
		const type = info.event.extendedProps.type;
		if (type !== 'available') {
			setError(new Error('That slot is already booked or reserved.'));
			return;
		}

		const eventStart = info.event.startStr.slice(0, 16);
		selectedSlot.value = {
			...info.event.extendedProps.slot,
			start_time: eventStart
		};
		selectedStartTime.value = eventStart;
		setMessage('Slot selected. You can reserve it or book immediately.');
	},
	allDaySlot: false
}));

function setMessage(text) {
	message.value = text;
	error.value = '';
}

function setError(err) {
	error.value = err.message || String(err);
	message.value = '';
}

function formatDate(value) {
	return value ? parseUtcDate(value).toLocaleString() : '';
}

function parseUtcDate(value) {
	if (!value) return null;
	return new Date(value.endsWith('Z') ? value : `${value}Z`);
}

async function loadAvailability() {
	if (!providerId.value) {
		setError(new Error('Enter a provider ID first.'));
		return;
	}

	try {
		const data = await apiRequest(
			`/api/availability/${providerId.value}?start_date=${startDate.value}&end_date=${endDate.value}`
		);
		availability.value = data.available_days || [];
		bookedSlots.value = data.booked_slots || [];
		selectedSlot.value = null;
		reservation.value = null;
		setMessage('Availability loaded.');
	} catch (err) {
		setError(err);
	}
}

function bookingPayload() {
	return {
		service_id: service.value.id,
		provider_id: providerId.value,
		start_time: selectedStartTime.value
	};
}

async function reserveSlot() {
	if (!selectedSlot.value || !service.value) return;

	try {
		reservation.value = await apiRequest('/api/bookings/reserve', {
			method: 'POST',
			body: JSON.stringify(bookingPayload())
		});
		bookedSlots.value.push(reservation.value);
		setMessage('Slot reserved. Confirm it before the hold expires.');
	} catch (err) {
		setError(err);
	}
}

async function confirmReservation() {
	if (!reservation.value) return;

	try {
		reservation.value = await apiRequest(`/api/bookings/${reservation.value.id}/confirm`, {
			method: 'PUT'
		});
		setMessage('Reservation confirmed.');
	} catch (err) {
		setError(err);
	}
}

async function bookSlot() {
	if (!selectedSlot.value || !service.value) return;

	try {
		const booking = await apiRequest('/api/bookings', {
			method: 'POST',
			body: JSON.stringify(bookingPayload())
		});
		bookedSlots.value.push(booking);
		selectedSlot.value = null;
		setMessage('Booking created.');
	} catch (err) {
		setError(err);
	}
}
</script>

<style>
.bookingControls {
	display: flex;
	flex-wrap: wrap;
	gap: 10px;
	margin-bottom: 16px;
}

.bookingControls label {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.selectedSlot {
	margin-top: 10px;
	font-weight: bold;
}
</style>
