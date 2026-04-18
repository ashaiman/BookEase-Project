<template>
	<div class="holdBanner">
		You have reserved a slot for : {{ Math.ceil(timeLeft/60) }} minutes. Please complete your booking.
	</div>
</template>

<script>
export default {
	props: ["timeLeft"],
	// data() {
	// 	return { timeLeft: 0, interval: null };
	// },
	// mounted() {
	// 	this.update();
	// 	this.interval = setInterval(this.update, 1000);
	// },
	// beforeUnmount() {
	// 	clearInterval(this.interval);
	// },
	// methods: {
	// 	update() {
	// 		this.timeLeft = Math.max(0, Math.floor((this.timeLeft - 1) / 1000) * 1000);
	// 	}
	// }
}
</script>

<style>
.holdBanner {
	background-color: #ffcc00;
	color: #333;
	padding: 10px;
	margin-bottom: 10px;
	border-radius: 6px;
	text-align: center;
	font-weight: bold;
}
</style>