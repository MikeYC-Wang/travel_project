import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ExchangeRate from '../views/ExchangeRate.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/exchange-rate',
    name: 'ExchangeRate',
    component: ExchangeRate
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router