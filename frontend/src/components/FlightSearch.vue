<script setup lang="ts">
import { ref } from 'vue'

const departure = ref('')
const destination = ref('')
const departDate = ref('')
const returnDate = ref('')
const passengers = ref(1)

// 模擬送出表單的動作
const searchFlights = () => {
  console.log('準備搜尋機票，條件：', {
    departure: departure.value,
    destination: destination.value,
    departDate: departDate.value,
    returnDate: returnDate.value,
    passengers: passengers.value
  })
  alert('準備開始搜尋機票！(目前為純前端畫面，稍後會串接後端 API)')
}
</script>

<template>
  <div class="flight-search-container">
    <form @submit.prevent="searchFlights" class="search-form">
      
      <div class="form-group">
        <label><font-awesome-icon icon="plane-departure" /> 出發地</label>
        <input type="text" v-model="departure" placeholder="例如：台北 (TPE)" required />
      </div>
      
      <div class="form-group">
        <label><font-awesome-icon icon="plane-arrival" /> 目的地</label>
        <input type="text" v-model="destination" placeholder="例如：東京 (NRT)" required />
      </div>
      
      <div class="form-group">
        <label><font-awesome-icon icon="calendar-days" /> 出發日期</label>
        <input type="date" v-model="departDate" required />
      </div>
      
      <div class="form-group">
        <label><font-awesome-icon icon="calendar-check" /> 回程日期</label>
        <input type="date" v-model="returnDate" />
      </div>

      <div class="form-group">
        <label><font-awesome-icon icon="user" /> 旅客</label>
        <div class="passenger-counter">
          <button type="button" class="counter-btn" @click="passengers > 1 ? passengers-- : null" :disabled="passengers <= 1">
            <font-awesome-icon icon="minus" />
          </button>
          
          <input type="number" v-model="passengers" min="1" readonly />
          
          <button type="button" class="counter-btn" @click="passengers++">
            <font-awesome-icon icon="plus" />
          </button>
        </div>
      </div>
      
      <div class="form-actions">
        <button type="submit" class="submit-btn">
          <font-awesome-icon icon="magnifying-glass" /> 尋找最便宜機票
        </button>
      </div>

    </form>
  </div>
</template>

<style src="../assets/css/FlightSearch.css"></style>