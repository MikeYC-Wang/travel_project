<script setup lang="ts">
import { ref } from 'vue'

// 定義行程的資料結構
interface Activity {
  id: number
  time: string
  title: string
  location: string
}

interface DayPlan {
  id: number
  dayNumber: number
  date: string
  activities: Activity[]
}

// 預設的假資料 (讓你一開始就有畫面看)
const itinerary = ref<DayPlan[]>([
  {
    id: 1,
    dayNumber: 1,
    date: '2026-05-10',
    activities: [
      { id: 101, time: '10:00', title: '抵達機場', location: '成田國際機場 (NRT)' },
      { id: 102, time: '13:30', title: '飯店 Check-in', location: '新宿格拉斯麗飯店' },
      { id: 103, time: '18:00', title: '晚餐：和牛燒肉', location: '敘敘苑 新宿中央東口店' }
    ]
  }
])

// 互動功能預留
const addDay = () => {
  const newDayNum = itinerary.value.length + 1
  itinerary.value.push({
    id: Date.now(),
    dayNumber: newDayNum,
    date: '', // 實務上這裡可以讓使用者選日期
    activities: []
  })
}

const addActivity = (dayId: number) => {
  const day = itinerary.value.find(d => d.id === dayId)
  if (day) {
    day.activities.push({
      id: Date.now(),
      time: '00:00',
      title: '新行程',
      location: '新地點'
    })
  }
}
</script>

<template>
  <div class="hero-section itinerary-section">
    <h1><font-awesome-icon icon="map-location-dot" /> 我的專屬行程表</h1>
    <p>輕鬆規劃每一天，讓完美旅程化為現實</p>

    <div class="itinerary-board">
      <div v-for="day in itinerary" :key="day.id" class="day-card">
        <div class="day-header">
          <h2>第 {{ day.dayNumber }} 天</h2>
          <span class="day-date"><font-awesome-icon icon="calendar-day" /> {{ day.date || '未設定日期' }}</span>
        </div>

        <div class="timeline">
          <div v-for="activity in day.activities" :key="activity.id" class="activity-item">
            <div class="activity-time">{{ activity.time }}</div>
            <div class="activity-content">
              <h3>{{ activity.title }}</h3>
              <p><font-awesome-icon icon="location-dot" /> {{ activity.location }}</p>
            </div>
            <button class="icon-btn edit-btn" title="編輯行程"><font-awesome-icon icon="pen" /></button>
          </div>
        </div>

        <button class="add-activity-btn" @click="addActivity(day.id)">
          <font-awesome-icon icon="plus" /> 新增行程
        </button>
      </div>
    </div>

    <div class="form-actions">
      <button class="submit-btn add-day-btn" @click="addDay">
        <font-awesome-icon icon="calendar-plus" /> 增加一天
      </button>
    </div>
  </div>
</template>

<style src="../assets/css/Itinerary.css"></style>