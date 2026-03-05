import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import cartService from '@/services/cart'
import type { ShoppingCartItemPublic, ShoppingCartItemCreateInCart } from '@/types/cart'

function extractErrorMessage(err: any, fallback: string): string {
  const detail = err?.data?.detail
  if (typeof detail === 'string') return detail

  const errors = detail?.errors
  if (typeof errors === 'string') return errors

  if (errors && typeof errors === 'object') {
    const messages: string[] = []

    for (const value of Object.values(errors)) {
      if (typeof value === 'string') {
        messages.push(value)
        continue
      }

      if (value && typeof value === 'object') {
        for (const nestedValue of Object.values(value)) {
          if (typeof nestedValue === 'string') {
            messages.push(nestedValue)
          }
        }
      }
    }

    if (messages.length > 0) {
      return messages.join(', ')
    }
  }

  return err?.message || fallback
}

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
      error.value = extractErrorMessage(err, 'Failed to fetch cart')
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
      error.value = extractErrorMessage(err, 'Failed to add item to cart')
      console.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function removeItem(itemId: number) {
    isLoading.value = true
    error.value = null
    try {
      await cartService.removeItem(itemId)
      items.value = items.value.filter((item) => item.id !== itemId)
    } catch (err: any) {
      error.value = extractErrorMessage(err, 'Failed to remove item')
      console.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateQuantity(itemId: number, qty: number) {
    if (qty < 1) return

    isLoading.value = true
    error.value = null
    try {
      await cartService.updateItemQty(itemId, { qty })
      const itemToUpdate = items.value.find((item) => item.id === itemId)
      if (itemToUpdate) {
        itemToUpdate.cart_qty = qty
      }
    } catch (err: any) {
      error.value = extractErrorMessage(err, 'Failed to update quantity')
      console.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function clearCart() {
    isLoading.value = true
    error.value = null
    try {
      await cartService.clearCart()
      items.value = []
    } catch (err: any) {
      error.value = extractErrorMessage(err, 'Failed to clear cart')
      console.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function checkout() {
    isLoading.value = true
    error.value = null
    try {
      await cartService.checkout()
      items.value = []
    } catch (err: any) {
      error.value = extractErrorMessage(err, 'Failed to checkout')
      console.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const getCartItemByProductId = (productId: number) => {
    //if (!Array.isArray(items.value)) return undefined
    return items.value.find((item) => item.product_id === productId)
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
    checkout,
    getCartItemByProductId,
  }
})
