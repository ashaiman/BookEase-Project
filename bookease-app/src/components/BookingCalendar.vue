
<template>
	<div class="BookingCalendar">
		<h1 v-if="service">Book: {{ service.name }}</h1>
		<p v-else>Loading service details...</p>

		<FullCalendar :options="calendarOptions" />

		<!-- Hold TImer -->
		<HoldTimer
			v-if="expiresAt"
			:expiresAt="expiresAt"
		/>

		<div v-if="selectedSlot" class="selectedSlot">
			Selected Slot: {{ selectedSlot}}
			<!-- Time: {{ selectedSlotTime }} -->
		</div>

		<button
			v-if="selectedSlot"
			@click="confirmBooking"
			class="confirmButton"
		>
			Confirm Booking
		</button>
	</div>
</template>

<script setup>
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { ref, computed } from 'vue';
import TimerHoldBanner from '../components/TimerHoldBanner.vue';
// import CalendarView from '../components/CalendarView.vue';

const calendarEvents = computed(() => {
	return availability.value.map(slot => ({
		id: slot.id,
		title: holds.value[slot.id] ? "Held" : 'Available',
		start: slot.date,
		// end: slot.date,
		color: holds.value[slot.id] ? "red" : "Green"
	}));
});

const calendarOptions = computed(() => ({
	plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
	initialView: 'dayGridMonth',

	headerToolbar: {
		left: 'prev,next today',
		center: 'title',
		right: 'dayGridMonth,timeGridWeek,timeGridDay'
	},

	events: calendarEvents.value,
	selectable: true,

	events: calendarEvents.value,

	eventClick(info) {
		handleSelectSlot(parseInt(info.event.id));
	},

	slotMinTime: "15:00:00",
	slotMaxTime: "45:00:00",
	allDaySlot: false

}));

// temp service
const service = ref({ id: 1, name: "Math Tutoring", duration: 60 });

// Temp data
const availability = ref([
	{ id: 1, date: "2026-07-01T10:00:00" },
	{ id: 2, date: "2026-07-01T11:00:00" },
	{ id: 3, date: "2026-07-01T14:00:00" }
]);

const holds = ref({}); // { slotId: expiresAt }
const selectedSlot = ref(null);
const expiresAt = ref(null);



function handleSelectSlot(slotId) {
	selectedSlot.value = slotId;
	
	const expireTime = Date.now() + 15 * 60 * 1000; // 15 minutes from now
	// holds.value[slotId] = expireTime;
	expiresAt.value = expireTime;

	holds.value[slotId] = true; // Mark as held
}

function confirmBooking() {
	if (!selectedSlot.value) return;

	// Here you would send a request to your backend to confirm the booking
	// For now, we'll just clear the hold and selected slot
	alert(`Booking confirmed for slot ${selectedSlot.value}!`);

	delete holds.value[selectedSlot.value];
	selectedSlot.value = null;
	expiresAt.value = null;
}

</script>

<style>
.booking-page {
  padding: 20px;
}

.confirm-btn {
  margin-top: 15px;
  padding: 10px 20px;
  background: #4caf50;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 6px;
}

.selected-slot {
  margin-top: 10px;
  font-weight: bold;
}
</style>
