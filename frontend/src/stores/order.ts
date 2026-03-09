import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Order } from '@/types/order'
import OrderService from '@/services/order'

export const useOrderStore = defineStore('order', () => {
  const orders = ref<Order[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function loadOrders(userId: number) {
    isLoading.value = true
    error.value = null

    try {
      orders.value = await OrderService.getOrders(userId)
      return orders.value
    } catch (err: any) {
      console.error('Failed to load orders:', err)
      error.value = err.message || 'Failed to fetch orders'
    } finally {
      isLoading.value = false
    }
  }

  return {
    orders,
    isLoading,
    error,
    loadOrders,
  }
})
