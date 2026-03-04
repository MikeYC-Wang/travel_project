<script setup lang="ts">
import { ref, onMounted } from 'vue'

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

const itinerary = ref<DayPlan[]>([])

// 1. 載入網頁時，去後端拿真實資料
const fetchItinerary = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/itinerary')
    itinerary.value = await response.json()
  } catch (error) {
    console.error("無法取得行程資料", error)
  }
}

onMounted(() => {
  fetchItinerary()
})

// 2. 增加一天 (打 POST API)
const addDay = async () => {
  const newDayNum = itinerary.value.length + 1
  await fetch('http://localhost:8000/api/itinerary/days', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ day_number: newDayNum, date: '' })
  })
  fetchItinerary() // 重新抓資料刷新畫面
}

// 3. 新增行程 (先彈出空的編輯視窗，把 id 設為 0 當作判斷)
const addActivity = (dayId: number) => {
  editingDayId.value = dayId
  editingActivity.value = { id: 0, time: '10:00', title: '', location: '' }
  showActivityModal.value = true
}

// ==================== 彈窗控制與儲存邏輯 ====================
const showActivityModal = ref(false)
const showDateModal = ref(false)

const editingActivity = ref<Activity | null>(null)
const editingDayId = ref<number | null>(null)
const editingDate = ref('')

const openActivityModal = (dayId: number, activity: Activity) => {
  editingDayId.value = dayId
  editingActivity.value = { ...activity }
  showActivityModal.value = true
}

// 4. 儲存行程 (判斷是新增還是更新)
const saveActivity = async () => {
  if (editingActivity.value && editingDayId.value) {
    const act = editingActivity.value
    
    if (act.id === 0) {
      // id 為 0，代表是新增 (POST)
      await fetch('http://localhost:8000/api/itinerary/activities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          day_id: editingDayId.value,
          time: act.time,
          title: act.title,
          location: act.location
        })
      })
    } else {
      // 有 id，代表是更新舊資料 (PUT)
      await fetch(`http://localhost:8000/api/itinerary/activities/${act.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          time: act.time,
          title: act.title,
          location: act.location
        })
      })
    }
  }
  closeModal()
  fetchItinerary() // 儲存完畢，刷新畫面
}

// 5. 刪除行程 (DELETE)
const deleteActivity = async () => {
  if (editingActivity.value && editingActivity.value.id !== 0) {
    if (confirm('確定要刪除這個行程嗎？')) {
      await fetch(`http://localhost:8000/api/itinerary/activities/${editingActivity.value.id}`, {
        method: 'DELETE'
      })
    }
  }
  closeModal()
  fetchItinerary()
}

const closeModal = () => {
  showActivityModal.value = false
  editingActivity.value = null
  editingDayId.value = null
}

const openDateModal = (day: DayPlan) => {
  editingDayId.value = day.id
  editingDate.value = day.date
  showDateModal.value = true
}

// 6. 儲存日期 (PUT)
const saveDate = async () => {
  if (editingDayId.value) {
    await fetch(`http://localhost:8000/api/itinerary/days/${editingDayId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date: editingDate.value })
    })
  }
  closeDateModal()
  fetchItinerary()
}

const closeDateModal = () => {
  showDateModal.value = false
  editingDayId.value = null
  editingDate.value = ''
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
          <span class="day-date" @click="openDateModal(day)" title="點擊設定日期">
            <font-awesome-icon icon="calendar-day" /> 
            {{ day.date || '設定日期' }}
            <font-awesome-icon icon="pen" class="date-edit-btn" />
          </span>
        </div>

        <div class="timeline">
          <div v-for="activity in day.activities" :key="activity.id" class="activity-item">
            <div class="activity-time">{{ activity.time }}</div>
            <div class="activity-content">
              <h3>{{ activity.title }}</h3>
              <p><font-awesome-icon icon="location-dot" /> {{ activity.location }}</p>
            </div>
            <button class="icon-btn edit-btn" title="編輯行程" @click="openActivityModal(day.id, activity)">
              <font-awesome-icon icon="pen" />
            </button>
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

    <div v-if="showActivityModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h3><font-awesome-icon icon="pen-to-square" /> 編輯行程</h3>
        
        <div class="form-group" v-if="editingActivity">
          <label>時間</label>
          <input type="time" v-model="editingActivity.time" />
        </div>
        <div class="form-group" v-if="editingActivity">
          <label>行程標題</label>
          <input type="text" v-model="editingActivity.title" placeholder="例如：抵達機場" />
        </div>
        <div class="form-group" v-if="editingActivity">
          <label>地點</label>
          <input type="text" v-model="editingActivity.location" placeholder="例如：成田國際機場" />
        </div>
        
        <div class="modal-actions">
          <button class="icon-btn delete-btn" @click="deleteActivity" title="刪除行程" style="margin-right: auto;">
            <font-awesome-icon icon="trash" />
          </button>
          <button class="cancel-btn" @click="closeModal">取消</button>
          <button class="save-btn" @click="saveActivity">儲存</button>
        </div>
      </div>
    </div>

    <div v-if="showDateModal" class="modal-overlay" @click.self="closeDateModal">
      <div class="modal-content date-modal">
        <h3><font-awesome-icon icon="calendar-day" /> 設定日期</h3>
        <div class="form-group">
          <label>選擇日期</label>
          <input type="date" v-model="editingDate" />
        </div>
        
        <div class="modal-actions">
          <button class="cancel-btn" @click="closeDateModal">取消</button>
          <button class="save-btn" @click="saveDate">儲存</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style src="../assets/css/Itinerary.css"></style>