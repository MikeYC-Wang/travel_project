<script setup lang="ts">
import { ref } from 'vue'

const currencies = ref([
  { code: 'TWD', name: '新台幣 (TWD)' },
  { code: 'JPY', name: '日圓 (JPY)' },
  { code: 'USD', name: '美元 (USD)' },
  { code: 'EUR', name: '歐元 (EUR)' },
  { code: 'KRW', name: '韓元 (KRW)' },
  { code: 'GBP', name: '英鎊 (GBP)' },
  { code: 'AUD', name: '澳幣 (AUD)' }
])

const amount = ref(100)
const fromCurrency = ref('TWD')
const toCurrency = ref('JPY')

const exchangeResult = ref<number | null>(null)
const currentRate = ref<number | null>(null)
const lastUpdate = ref<string>('') // 👈 新增：用來存最後更新時間
const isLoading = ref(false)

const swapCurrencies = () => {
  const temp = fromCurrency.value
  fromCurrency.value = toCurrency.value
  toCurrency.value = temp
  exchangeResult.value = null 
}

const calculateRate = async () => {
  if (amount.value <= 0) return
  
  isLoading.value = true
  exchangeResult.value = null
  
  try {
    const response = await fetch(`http://localhost:8000/api/exchange?amount=${amount.value}&from_currency=${fromCurrency.value}&to_currency=${toCurrency.value}`)
    const data = await response.json()
    
    if (data.status === 'success') {
      exchangeResult.value = data.converted_amount
      currentRate.value = data.rate
      
      // 👈 新增：將後端傳來的 UTC 時間轉換為台灣當地的易讀格式
      const dateObj = new Date(data.last_update)
      lastUpdate.value = dateObj.toLocaleString('zh-TW', { 
        year: 'numeric', month: '2-digit', day: '2-digit', 
        hour: '2-digit', minute: '2-digit', hour12: false 
      })
    } else {
      alert('計算失敗：' + data.detail)
    }
  } catch (error) {
    alert('無法連線到後端 API，請確認 FastAPI 是否有啟動！')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="hero-section">
    <h1>即時匯率計算機</h1>
    <p>隨時掌握最新匯率，旅遊預算不超支</p>
    
    <div class="exchange-container">
      <form @submit.prevent="calculateRate" class="exchange-form">
        <div class="form-group amount-group">
          <label><font-awesome-icon icon="money-bill-wave" /> 金額</label>
          <input type="number" v-model="amount" min="1" required />
        </div>

        <div class="form-group">
          <label><font-awesome-icon icon="wallet" /> 原始幣別</label>
          <div class="select-wrapper">
            <select v-model="fromCurrency">
              <option v-for="currency in currencies" :key="currency.code" :value="currency.code">{{ currency.name }}</option>
            </select>
          </div>
        </div>

        <div class="swap-btn-container">
          <button type="button" class="swap-btn" @click="swapCurrencies" title="反轉幣別">
            <font-awesome-icon icon="right-left" />
          </button>
        </div>

        <div class="form-group">
          <label><font-awesome-icon icon="globe" /> 目標幣別</label>
          <div class="select-wrapper">
            <select v-model="toCurrency">
              <option v-for="currency in currencies" :key="currency.code" :value="currency.code">{{ currency.name }}</option>
            </select>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="submit-btn" :disabled="isLoading">
            <font-awesome-icon :icon="isLoading ? 'spinner' : 'calculator'" :spin="isLoading" /> 
            {{ isLoading ? '計算中...' : '計算匯率' }}
          </button>
        </div>
      </form>

      <div v-if="exchangeResult !== null" class="result-box">
        <div class="result-content">
          <span class="original">{{ amount }} {{ fromCurrency }} =</span>
          <span class="converted">{{ exchangeResult.toLocaleString() }} {{ toCurrency }}</span>
        </div>
        <div class="rate-info">
          當前匯率：1 {{ fromCurrency }} = {{ currentRate }} {{ toCurrency }}
        </div>
        
        <div class="disclaimer">
          <font-awesome-icon icon="circle-info" /> 
          此為全球中價匯率，僅供行程預算參考，實際換匯請依各銀行之牌告/即期匯率為準。<br>
          資料最後更新時間：{{ lastUpdate }}
        </div>
      </div>

    </div>
  </div>
</template>

<style src="../assets/css/ExchangeRate.css"></style>