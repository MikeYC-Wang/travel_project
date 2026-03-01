<script setup lang="ts">
import { ref, onMounted } from 'vue'

const siteName = ref('旅人日誌')
// 用來記錄目前是否為深色模式
const isDarkMode = ref(false)

// 切換主題的函式
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  const theme = isDarkMode.value ? 'dark' : 'light'
  
  // 在 HTML 根元素加上 data-theme 屬性，觸發 theme.css 的深色變數
  document.documentElement.setAttribute('data-theme', theme)
  // 把設定存起來，下次進網頁才不會跑掉
  localStorage.setItem('site-theme', theme)
}

// 網頁一載入時，先去檢查之前有沒有存過設定
onMounted(() => {
  const savedTheme = localStorage.getItem('site-theme')
  if (savedTheme === 'dark') {
    isDarkMode.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  }
})
</script>

<template>
  <div class="app-wrapper">
    <nav class="navbar">
      <div class="logo">
        <font-awesome-icon icon="compass" /> {{ siteName }}
      </div>
      <ul class="nav-links">
        <li><a href="#" class="active"><font-awesome-icon icon="house" /> 首頁</a></li>
        <li><a href="#"><font-awesome-icon icon="plane-departure" /> 找機票</a></li>
        <li><a href="#"><font-awesome-icon icon="coins" /> 看匯率</a></li>
        <li><a href="#"><font-awesome-icon icon="map-location-dot" /> 排行程</a></li>
        
        <li>
          <a href="#" @click.prevent="toggleTheme">
            <font-awesome-icon :icon="isDarkMode ? 'sun' : 'moon'" />
            {{ isDarkMode ? 'Light' : 'Dark' }}
          </a>
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