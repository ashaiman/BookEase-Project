


<template>
  <div id="app">
    <MenuBar

      :user="user"
      @navigate="handleNavigation"
      @logout="logoutUser"
    />

    <div class="page">
      <component 
        :is="currentView"
        @navigate="handleNavigation"
        :selectedService="selectedService"
        :user="user"
        @selectService="handleServiceSelection"
      />
    </div>
  </div>
</template>

<script setup>

import { ref } from 'vue';

// import * as MenuBarTest from './components/MenuBar.vue';
// console.log(MenuBarTest);
import MenuBar from './components/MenuBar.vue';
import LoginForm from './components/LoginForm.vue';
import HomeView from './components/HomeView.vue';
// import ServiceCard from './components/ServiceCard.vue';
import BookingCalendar from './components/BookingCalendar.vue';
import Dashboard from './components/Dashboard.vue';
// import MenuBar from './components/MenuBar.vue';
// import style.css from './style.css';

const views = {
  LoginForm,
  HomeView,
  // ServiceDetail,
  // ServiceCard,
  BookingCalendar,
  Dashboard
};

const selectedService = ref(null);
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'));
const currentView = ref(user.value ? HomeView : LoginForm);

function handleNavigation(view, payload) {
  if (payload?.user) user.value = payload.user;
  if (payload?.service) selectedService.value = payload.service;

  const nextView = views[view];

  if (nextView) {
    currentView.value = nextView;
  } else {
    console.warn(`Unknown view: ${view}`);
    currentView.value = LoginForm;
  }
  // currentView.value = views[view];
}

function handleServiceSelection(service) {
  selectedService.value = service;
  currentView.value = views.BookingCalendar;
}

function logoutUser() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  user.value = null;
  currentView.value = views.LoginForm;
}

// export default {
//   components: {
//     LoginForm,
//     HomeView,
//     ServiceDetail,
//     BookingCalendar,
//     Dashboard,
//     MenuBar
//   },
//   data() {
//     return {
//       currentView: 'LoginForm',
//       selectedService: null,
//     };
//   },
//   methods: {
//     handleNavigation(view, payload) {
//       if (payload?.user) this.user = payload.user;
//       if (payload?.service) this.selectedService = payload.service;
//       this.currentView = view;
//     },
//     handleServiceSelection(service) {
//       this.selectedService = service;
//       this.currentView = 'ServiceDetail';
//     }
//   }
// };
</script>

<!-- <template>
	<div class="LoginPage">
		<LoginForm />
	</div>
</template> -->





<!-- <template>
  <div>
    <a href="https://vite.dev" target="_blank">
      <img src="/vite.svg" class="logo" alt="Vite logo" />
    </a>
    <a href="https://vuejs.org/" target="_blank">
      <img src="./assets/vue.svg" class="logo vue" alt="Vue logo" />
    </a>
  </div>
  <HelloWorld msg="Vite + Vue" />
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style> -->

<style>
.page {
  padding-top: 50px;
}

body {
  margin: 0;
}
</style>
