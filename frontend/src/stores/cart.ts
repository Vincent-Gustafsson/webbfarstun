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
      items.value = data.items
    } catch (err: any) {
      // FIXED: using err.data to match your custom http.ts wrapper
      error.value = err.data?.detail || err.message || 'Failed to fetch cart'
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
      // Backend returns the fully updated cart on POST
      items.value = data.items
    } catch (err: any) {
      error.value = err.data?.detail?.errors || err.message || 'Failed to add item to cart'
      console.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // NEW: Remove item
  async function removeItem(itemId: number) {
    isLoading.value = true
    error.value = null
    try {
      await cartService.removeItem(itemId)
      // Backend returns 204 No Content, so we update the local state to match
      items.value = items.value.filter((item) => item.id !== itemId)
    } catch (err: any) {
      error.value = err.data?.detail?.errors || err.message || 'Failed to remove item'
      console.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // NEW: Update item quantity
  async function updateQuantity(itemId: number, qty: number) {
    if (qty < 1) return // Matches your backend validation rule

    isLoading.value = true
    error.value = null
    try {
      await cartService.updateItemQty(itemId, { qty })
      // Backend returns 204 No Content, so we update the specific item locally
      const itemToUpdate = items.value.find((item) => item.id === itemId)
      if (itemToUpdate) {
        itemToUpdate.cart_qty = qty
      }
    } catch (err: any) {
      error.value = err.data?.detail?.errors || err.message || 'Failed to update quantity'
      console.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // UPDATED: Clear the entire cart from the database
  async function clearCart() {
    isLoading.value = true
    error.value = null
    try {
      await cartService.clearCart()
      items.value = [] // Clear state only after backend confirms deletion
    } catch (err: any) {
      error.value = err.data?.detail || err.message || 'Failed to clear cart'
      console.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    items,
    isLoading,
    error,
    cartTotal,
    totalItemsCount,
    fetchCart,
    addToCart,
    removeItem,
    updateQuantity,
    clearCart,
  }
})
