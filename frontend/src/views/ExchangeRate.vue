<script setup lang="ts">
import { ref } from 'vue'

// 定義支援的幣別清單
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

// 一鍵反轉幣別的函式
const swapCurrencies = () => {
  const temp = fromCurrency.value
  fromCurrency.value = toCurrency.value
  toCurrency.value = temp
}

// 模擬送出計算
const calculateRate = () => {
  console.log(`準備計算匯率：${amount.value} ${fromCurrency.value} 轉換為 ${toCurrency.value}`)
  alert('準備取得即時匯率！(稍後會串接後端 API)')
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
              <option v-for="currency in currencies" :key="currency.code" :value="currency.code">
                {{ currency.name }}
              </option>
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
              <option v-for="currency in currencies" :key="currency.code" :value="currency.code">
                {{ currency.name }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="submit-btn">
            <font-awesome-icon icon="calculator" /> 計算匯率
          </button>
        </div>

      </form>
    </div>
  </div>
</template>

<style src="../assets/css/ExchangeRate.css"></style>