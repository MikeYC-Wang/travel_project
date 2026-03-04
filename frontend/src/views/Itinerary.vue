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

const addDay = () => {
  const newDayNum = itinerary.value.length + 1
  itinerary.value.push({
    id: Date.now(),
    dayNumber: newDayNum,
    date: '',
    activities: []
  })
}

// 新增行程時，直接自動打開編輯彈窗
const addActivity = (dayId: number) => {
  const day = itinerary.value.find(d => d.id === dayId)
  if (day) {
    const newActivity = {
      id: Date.now(),
      time: '00:00',
      title: '新行程',
      location: '新地點'
    }
    day.activities.push(newActivity)
    openActivityModal(day.id, newActivity) // 👈 新增完自動彈出讓使用者改
  }
}

// ==================== 彈窗控制邏輯 ====================
const showActivityModal = ref(false)
const showDateModal = ref(false)

const editingActivity = ref<Activity | null>(null)
const editingDayId = ref<number | null>(null)
const editingDate = ref('')

// 1. 打開「行程」編輯彈窗
const openActivityModal = (dayId: number, activity: Activity) => {
  editingDayId.value = dayId
  // 💡 重點：使用淺拷貝 { ...activity }，這樣在彈窗打字時才不會直接影響到底下的畫面
  editingActivity.value = { ...activity }
  showActivityModal.value = true
}

// 儲存行程
const saveActivity = () => {
  if (editingDayId.value && editingActivity.value) {
    const day = itinerary.value.find(d => d.id === editingDayId.value)
    if (day) {
      const index = day.activities.findIndex(a => a.id === editingActivity.value!.id)
      if (index !== -1) {
        day.activities[index] = { ...editingActivity.value } // 把改好的資料覆蓋回去
      }
    }
  }
  closeModal()
}

// 刪除行程
const deleteActivity = () => {
  if (editingDayId.value && editingActivity.value) {
    const day = itinerary.value.find(d => d.id === editingDayId.value)
    if (day) {
      day.activities = day.activities.filter(a => a.id !== editingActivity.value!.id)
    }
  }
  closeModal()
}

const closeModal = () => {
  showActivityModal.value = false
  editingActivity.value = null
  editingDayId.value = null
}

// 2. 打開「日期」編輯彈窗
const openDateModal = (day: DayPlan) => {
  editingDayId.value = day.id
  editingDate.value = day.date
  showDateModal.value = true
}

// 儲存日期
const saveDate = () => {
  if (editingDayId.value) {
    const day = itinerary.value.find(d => d.id === editingDayId.value)
    if (day) {
      day.date = editingDate.value
    }
  }
  closeDateModal()
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