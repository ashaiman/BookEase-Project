<template>
	<div class="BookingCalendar">
		<section class="bookingHero" v-if="service">
			<div>
				<h1>{{ service.name }}</h1>
				<p>{{ service.description || 'Choose a provider, load availability, and select a start time.' }}</p>
			</div>
			<div class="heroMeta">
				<span class="tag">{{ service.category || 'uncategorized' }}</span>
				<span class="tag">{{ service.duration }} minutes</span>
			</div>
		</section>
		<p v-else class="emptyState">Select a service from Home first.</p>
		<div v-if="message" class="statusBanner">{{ message }}</div>
		<div v-if="error" class="statusBanner errorBanner">{{ error }}</div>

		<div v-if="service" class="bookingControls">
			<div class="stepCard">
				<span class="stepNumber">1</span>
				<div>
					<h3>Choose a provider</h3>
					<p>Select a provider who offers this service.</p>
				</div>
				<label>
					<span>Provider</span>
					<select v-model="providerId">
						<option value="">Select a provider</option>
						<option v-for="provider in providers" :key="provider.id" :value="provider.id">
							{{ provider.username }} (ID {{ provider.id }})
						</option>
					</select>
				</label>
			</div>

			<div class="stepCard">
				<span class="stepNumber">2</span>
				<div>
					<h3>Load availability</h3>
					<p>Choose a date range that includes your desired appointment day.</p>
				</div>
				<div class="dateFields">
					<label>
						<span>Start date</span>
						<input v-model="startDate" type="date" />
					</label>
					<label>
						<span>End date</span>
						<input v-model="endDate" type="date" />
					</label>
				</div>
				<button @click="loadAvailability">Load Availability</button>
			</div>
		</div>

		<FullCalendar :options="calendarOptions" />

		<TimerHoldBanner
			v-if="reservation?.reserved_until"
			:timeLeft="reservationSecondsLeft"
		/>

		<div v-if="selectedSlot" class="selectedSlot">
			<div>
				<h3>3. Choose an appointment time</h3>
				<p>Selected window: {{ selectedSlot.date }} {{ selectedSlot.start_time }}-{{ selectedSlot.end_time }}</p>
			</div>
			<label>
				<span>Appointment start time</span>
				<input v-model="selectedStartTime" type="datetime-local" />
			</label>
			<div class="actionRow">
				<button class="secondaryButton" @click="reserveSlot">Reserve 15-Minute Hold</button>
				<button @click="bookSlot">Book Immediately</button>
			</div>
		</div>

		<div v-if="reservation" class="reservationCard">
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
import { computed, ref, watch } from 'vue';
import { apiRequest } from '../api';
import TimerHoldBanner from '../components/TimerHoldBanner.vue';

const props = defineProps({
	selectedService: Object,
	user: Object
});

const service = computed(() => props.selectedService);
const providerId = ref('');
const providers = ref([]);
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
		setError(new Error('Choose a provider first.'));
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

async function loadProviders() {
	if (!service.value?.id) return;

	try {
		providers.value = await apiRequest(`/api/services/${service.value.id}/providers`);
		if (providers.value.length === 1) {
			providerId.value = providers.value[0].id;
		}
	} catch (err) {
		setError(err);
	}
}

function bookingPayload() {
	return {
		service_id: service.value.id,
		provider_id: Number(providerId.value),
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

watch(
	() => service.value?.id,
	() => {
		providers.value = [];
		providerId.value = '';
		selectedSlot.value = null;
		selectedStartTime.value = '';
		availability.value = [];
		bookedSlots.value = [];
		reservation.value = null;
		loadProviders();
	},
	{ immediate: true }
);
</script>

<style>
.bookingControls {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 16px;
	margin-bottom: 22px;
}

.bookingControls label,
.selectedSlot label {
	display: flex;
	flex-direction: column;
	gap: 4px;
	font-weight: 600;
	color: #5d4a53;
}

.bookingHero {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 20px;
	background: #ffffff;
	border: 1px solid #ecd6de;
	border-radius: 16px;
	box-shadow: 0 16px 32px rgba(198, 120, 145, 0.1);
	padding: 22px 24px;
}

.bookingHero h1 {
	margin-bottom: 0.35rem;
}

.stepCard,
.selectedSlot {
	padding: 18px 20px;
	background: #ffffff;
	border: 1px solid #ecd6de;
	border-radius: 16px;
	box-shadow: 0 16px 32px rgba(198, 120, 145, 0.1);
	display: grid;
	gap: 12px;
	font-weight: 600;
}

.stepCard {
	display: grid;
	gap: 12px;
	align-content: start;
}

.stepCard h3,
.selectedSlot h3 {
	margin-bottom: 0.25rem;
}

.stepCard p,
.selectedSlot p,
.bookingHero p,
.reservationCard p {
	margin: 0;
	color: #6f5e66;
}

.stepNumber {
	width: 34px;
	height: 34px;
	border-radius: 999px;
	display: inline-flex;
	align-items: center;
	justify-content: center;
	background: #ef9fb4;
	color: white;
	font-weight: 700;
}

.dateFields {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 12px;
}

.heroMeta,
.actionRow {
	display: flex;
	flex-wrap: wrap;
	gap: 10px;
}

.reservationCard {
	background: #ffffff;
	border: 1px solid #ecd6de;
	border-radius: 16px;
	padding: 18px 20px;
	box-shadow: 0 16px 32px rgba(198, 120, 145, 0.1);
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 16px;
}

.BookingCalendar {
	max-width: 1120px;
	margin: 0 auto;
	display: grid;
	gap: 18px;
}

.BookingCalendar h1,
.BookingCalendar > p {
	text-align: center;
}

.secondaryButton {
	background: #f7dbe4;
	color: #8b4f63;
}

.secondaryButton:hover {
	background: #efc9d5;
}

.tag {
	display: inline-flex;
	align-items: center;
	padding: 0.45rem 0.8rem;
	border-radius: 999px;
	background: #fff1f5;
	color: #8b4f63;
	font-size: 0.92rem;
	font-weight: 600;
}

@media (max-width: 900px) {
	.bookingControls,
	.dateFields {
		grid-template-columns: 1fr;
	}

	.bookingHero,
	.reservationCard {
		flex-direction: column;
		align-items: stretch;
	}
}
</style>
