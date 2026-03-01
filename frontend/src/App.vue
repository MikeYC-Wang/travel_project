<script setup lang="ts">
import { ref } from 'vue'

const siteName = ref('旅人日誌')
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

<style scoped src="./assets/css/App.css"></style>