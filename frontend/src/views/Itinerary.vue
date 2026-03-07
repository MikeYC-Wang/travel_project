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

const addDay = async () => {
  const newDayNum = itinerary.value.length + 1
  await fetch('http://localhost:8000/api/itinerary/days', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ day_number: newDayNum, date: '' })
  })
  fetchItinerary()
}

const addActivity = (dayId: number) => {
  editingDayId.value = dayId
  editingActivity.value = { id: 0, time: '10:00', title: '', location: '' }
  showActivityModal.value = true
}

// ==================== 彈窗控制邏輯 ====================
const showActivityModal = ref(false)
const showDateModal = ref(false)
const showAiModal = ref(false) 
const showSingleAiModal = ref(false) 

const editingActivity = ref<Activity | null>(null)
const editingDayId = ref<number | null>(null)
const editingDate = ref('')

// ==================== AI 全局設定變數 ====================
const aiDestination = ref('') // 👈 這裡已經清空，沒有預設的東京了
const aiDays = ref(3)
const aiStartDate = ref('')
const aiArrivalTime = ref('') 
const aiNotes = ref('')       
const isAiLoading = ref(false)

// ==================== AI 單日設定變數 ====================
const singleAiDayId = ref<number | null>(null)
const singleAiDestination = ref('') // 讓單日重排也能獨立設定地點
const singleAiNotes = ref('')
const isSingleAiLoading = ref(false)

// 🚀 呼叫後端 AI 生成 API (全局)
const generateAiItinerary = async () => {
  if (!aiDestination.value || aiDays.value < 1 || !aiStartDate.value) {
    alert('請完整填寫目的地、天數與出發日期！')
    return
  }

  isAiLoading.value = true
  try {
    const response = await fetch('http://localhost:8000/api/itinerary/ai-generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        destination: aiDestination.value,
        days: aiDays.value,
        start_date: aiStartDate.value,
        arrival_time: aiArrivalTime.value || null,
        notes: aiNotes.value || null
      })
    })

    const data = await response.json()
    if (data.status === 'success') {
      showAiModal.value = false
      await fetchItinerary() 
      
      // 生成完畢後，不清空目的地，保留給單日重排使用，只清空其他設定
      aiDays.value = 3
      aiStartDate.value = ''
      aiArrivalTime.value = ''
      aiNotes.value = ''
    } else {
      alert('AI 生成失敗：' + data.detail)
    }
  } catch (error) {
    alert('無法連線到後端 API！')
  } finally {
    isAiLoading.value = false
  }
}

// 🚀 開啟單日 AI 彈窗
const openSingleAiModal = (dayId: number) => {
  singleAiDayId.value = dayId
  // 自動帶入你剛剛在全局設定的目的地，方便你不用重打，但你可以自由修改
  singleAiDestination.value = aiDestination.value 
  singleAiNotes.value = ''
  showSingleAiModal.value = true
}

// 🚀 呼叫後端 AI 重新生成 (單日)
const generateSingleDayAi = async () => {
  if (!singleAiDayId.value || !singleAiDestination.value) {
    alert('請輸入這天的目的地！')
    return
  }
  
  isSingleAiLoading.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/itinerary/days/${singleAiDayId.value}/ai-regenerate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        destination: singleAiDestination.value, // 使用單獨的目的地
        notes: singleAiNotes.value || null
      })
    })
    const data = await response.json()
    if (data.status === 'success') {
      showSingleAiModal.value = false
      await fetchItinerary()
    } else {
      alert('AI 重排失敗：' + data.detail)
    }
  } catch (error) {
    alert('連線失敗！')
  } finally {
    isSingleAiLoading.value = false
  }
}

const openActivityModal = (dayId: number, activity: Activity) => {
  editingDayId.value = dayId
  editingActivity.value = { ...activity }
  showActivityModal.value = true
}

const saveActivity = async () => {
  if (editingActivity.value && editingDayId.value) {
    const act = editingActivity.value
    if (act.id === 0) {
      await fetch('http://localhost:8000/api/itinerary/activities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ day_id: editingDayId.value, time: act.time, title: act.title, location: act.location })
      })
    } else {
      await fetch(`http://localhost:8000/api/itinerary/activities/${act.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ time: act.time, title: act.title, location: act.location })
      })
    }
  }
  closeModal()
  fetchItinerary()
}

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

    <div class="top-actions">
      <button class="ai-btn" @click="showAiModal = true">
        <font-awesome-icon icon="wand-magic-sparkles" /> AI 智能排行程
      </button>
      <button class="submit-btn add-day-btn-top" @click="addDay">
        <font-awesome-icon icon="calendar-plus" /> 增加一天
      </button>
    </div>

    <div class="itinerary-board">
      <div v-if="itinerary.length === 0" class="empty-state">
        <font-awesome-icon icon="box-open" size="3x" />
        <p>目前還沒有行程喔！點擊上方按鈕開始規劃吧！</p>
      </div>

      <div v-for="day in itinerary" :key="day.id" class="day-card">
        <div class="day-header">
          <div style="display: flex; align-items: center; gap: 15px;">
            <h2>第 {{ day.dayNumber }} 天</h2>
            <span class="day-date" @click="openDateModal(day)" title="點擊設定日期">
              <font-awesome-icon icon="calendar-day" /> 
              {{ day.date || '設定日期' }}
              <font-awesome-icon icon="pen" class="date-edit-btn" />
            </span>
          </div>
          <button class="ai-btn-small" @click="openSingleAiModal(day.id)" title="讓AI重排這一天">
            <font-awesome-icon icon="rotate" /> AI 重排此日
          </button>
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

    <div v-if="showAiModal" class="modal-overlay" @click.self="!isAiLoading ? showAiModal = false : null">
      <div class="modal-content ai-modal">
        <h3><font-awesome-icon icon="wand-magic-sparkles" /> 讓 AI 為您規劃</h3>
        <p class="ai-desc">輸入您的需求，AI 將自動為您生成每日行程與推薦景點！</p>
        
        <div class="form-group">
          <label>目的地</label>
          <input type="text" v-model="aiDestination" placeholder="例如：東京、巴黎、首爾" :disabled="isAiLoading" />
        </div>
        
        <div class="form-row">
          <div class="form-group half">
            <label>旅遊天數</label>
            <input type="number" v-model="aiDays" min="1" max="14" :disabled="isAiLoading" />
          </div>
          <div class="form-group half">
            <label>出發日期</label>
            <input type="date" v-model="aiStartDate" :disabled="isAiLoading" />
          </div>
        </div>

        <div class="form-group">
          <label>抵達時間 (選填)</label>
          <input type="time" v-model="aiArrivalTime" :disabled="isAiLoading" />
        </div>

        <div class="form-group">
          <label>特別需求與備註 (選填)</label>
          <textarea v-model="aiNotes" placeholder="例如：第一天想去吃和牛、行程不要排太緊..." rows="3" :disabled="isAiLoading"></textarea>
        </div>
        
        <div class="modal-actions">
          <button class="cancel-btn" @click="showAiModal = false" :disabled="isAiLoading">取消</button>
          <button class="ai-submit-btn" @click="generateAiItinerary" :disabled="isAiLoading">
            <font-awesome-icon :icon="isAiLoading ? 'spinner' : 'robot'" :spin="isAiLoading" /> 
            {{ isAiLoading ? 'AI 腦力激盪中...' : '開始生成' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showSingleAiModal" class="modal-overlay" @click.self="!isSingleAiLoading ? showSingleAiModal = false : null">
      <div class="modal-content ai-modal">
        <h3><font-awesome-icon icon="rotate" /> AI 單日重新規劃</h3>
        <p class="ai-desc">告訴 AI 您對這天的想法，讓它專門為這一天重新排程！</p>
        
        <div class="form-group">
          <label>單日目的地</label>
          <input type="text" v-model="singleAiDestination" placeholder="例如：富士山、河口湖" :disabled="isSingleAiLoading" />
        </div>

        <div class="form-group">
          <label>修改需求 / 備註</label>
          <textarea v-model="singleAiNotes" placeholder="例如：這天想安排整天在迪士尼、想去逛秋葉原..." rows="3" :disabled="isSingleAiLoading"></textarea>
        </div>
        
        <div class="modal-actions">
          <button class="cancel-btn" @click="showSingleAiModal = false" :disabled="isSingleAiLoading">取消</button>
          <button class="ai-submit-btn" @click="generateSingleDayAi" :disabled="isSingleAiLoading">
            <font-awesome-icon :icon="isSingleAiLoading ? 'spinner' : 'wand-magic-sparkles'" :spin="isSingleAiLoading" /> 
            {{ isSingleAiLoading ? '重排中...' : '重新生成這天' }}
          </button>
        </div>
      </div>
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