import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import cartService from '@/services/cart'
import type { ShoppingCartItemPublic, ShoppingCartItemCreateInCart } from '@/types/cart'

export const useCartStore = defineStore('cart', () => {
  const items = ref<ShoppingCartItemPublic[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const cartTotal = computed(() => {
    return items.value.reduce((total, item) => {
      return total + item.price * item.cart_qty
    }, 0)
  })

  const totalItemsCount = computed(() => {
    return items.value.reduce((count, item) => {
      return count + item.cart_qty
    }, 0)
  })

  async function fetchCart() {
    isLoading.value = true
    error.value = null
    try {
      const data = await cartService.getCart()
      // Note: adjust 'data.items' if your http client wraps responses (e.g., data.data.items for raw Axios)
      items.value = data.items
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch cart'
      console.error(error.value)
    } finally {
      isLoading.value = false
    }
  }

  async function addToCart(payload: ShoppingCartItemCreateInCart) {
    isLoading.value = true
    error.value = null
    try {
      const data = await cartService.addItem(payload)
      // Your backend returns the fully updated cart on POST /items,
      // so we can just replace the current state directly!
      items.value = data.items
    } catch (err: any) {
      // Handles the 400 Validation errors from your FastAPI route
      error.value = err.response?.data?.detail?.errors || 'Failed to add item to cart'
      console.error(error.value)
      throw err // Optional: re-throw if you want to show a UI toast notification in the component
    } finally {
      isLoading.value = false
    }
  }

  function clearCart() {
    items.value = []
    error.value = null
  }

  return {
    items,
    isLoading,
    error,
    cartTotal,
    totalItemsCount,
    fetchCart,
    addToCart,
    clearCart,
  }
})
