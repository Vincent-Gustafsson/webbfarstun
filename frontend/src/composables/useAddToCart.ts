import { computed } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'

export function useAddToCart(
  getProductId: () => number | undefined,
  isCompleteSelection: () => boolean,
) {
  const cartStore = useCartStore()
  const userStore = useUserStore()

  const isAlreadyInCart = computed(() => {
    const id = getProductId()
    if (!id) return false
    return !!cartStore.getCartItemByProductId(id)
  })

  const tooltipString = computed(() => {
    if (!userStore.isLoggedIn) return 'You must be logged in'
    if (isAlreadyInCart.value) return 'Already in your cart'
    return ''
  })

  const isButtonDisabled = computed(() => {
    const id = getProductId()
    return !id || !isCompleteSelection() || !userStore.isLoggedIn || isAlreadyInCart.value
  })

  async function handleAdd() {
    const id = getProductId()
    if (isButtonDisabled.value || !id) return

    try {
      await cartStore.addToCart({ product_id: id, qty: 1 })
    } catch (err) {
      console.error(`Failed to add product ${id}:`, err)
    }
  }

  return { tooltipString, isButtonDisabled, handleAdd }
}
