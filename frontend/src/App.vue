<script setup lang="ts">
import { ref, onMounted } from 'vue'

const siteName = ref('旅人日誌')
const isDark = ref(false)

const toggleTheme = () => {
  isDark.value = !isDark.value
  const theme = isDark.value ? 'dark' : 'light'
  
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('site-theme', theme)
}

onMounted(() => {
  const savedTheme = localStorage.getItem('site-theme')
  if (savedTheme === 'dark') {
    isDark.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  }
})
</script>

<template>
  <div class="app-wrapper">
    <nav class="navbar">
      <div class="logo">
        <font-awesome-icon icon="plane" /> {{ siteName }}
      </div>
      <ul class="nav-links">
        <li><a href="#" class="active"><font-awesome-icon icon="house" /> 首頁</a></li>
        <li><a href="#"><font-awesome-icon icon="plane-departure" /> 找機票</a></li>
        <li><a href="#"><font-awesome-icon icon="coins" /> 看匯率</a></li>
        <li><a href="#"><font-awesome-icon icon="map-location-dot" /> 排行程</a></li>
        
        <li>
          <button class="theme-btn" @click="toggleTheme" :title="isDark ? '切換到淺色模式' : '切換到深色模式'">
            <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
            <span class="btn-text">{{ isDark ? 'Dark' : 'Light' }}</span>
          </button>
        </li>
      </ul>
    </nav>

    <main class="main-content">
      <div class="hero-section">
        <h1>準備好你的下一趟旅程了嗎？</h1>
        <p>整合最划算機票、即時匯率與智能行程規劃的一站式服務</p>
      </div>
    </main>
  </div>
</template>

<style src="./assets/css/App.css"></style>