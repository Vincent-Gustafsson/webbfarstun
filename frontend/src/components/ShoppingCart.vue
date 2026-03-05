<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'
import { productImageUrl } from '@/services/products.ts'

const users = useUserStore()
const cartStore = useCartStore()
const isCartOpen = ref(false)

const toggleCart = () => (isCartOpen.value = !isCartOpen.value)
const closeCart = () => (isCartOpen.value = false)

onMounted(() => {
  cartStore.fetchCart()
})

// Logic to remove an item
const handleRemove = async (itemId: number) => {
  try {
    await cartStore.removeItem(itemId)
  } catch (err) {
    // Error is already handled/logged in the store
  }
}

// Logic to update quantity (Plus/Minus)
const handleUpdateQty = async (itemId: number, currentQty: number, delta: number) => {
  const newQty = currentQty + delta
  if (newQty > 0) {
    await cartStore.updateQuantity(itemId, newQty)
  } else {
    // If quantity goes to 0, we can just remove it
    handleRemove(itemId)
  }
}

const handleClearCart = async () => {
  await cartStore.clearCart()
}
</script>

<template>
  <div class="relative">
    <Transition name="fade">
      <div
        v-if="isCartOpen"
        @click="closeCart"
        class="fixed inset-0 z-40 bg-neutral/60 transition-all"
      ></div>
    </Transition>

    <div :class="['dropdown dropdown-end', { 'dropdown-open': isCartOpen }]">
      <button
        type="button"
        class="btn btn-primary relative z-50"
        @click="toggleCart"
        :disabled="!users.isLoggedIn || (cartStore.isLoading && items.length === 0)"
      >
        <span v-if="cartStore.isLoading" class="loading loading-spinner loading-xs"></span>
        Cart
        <div v-if="cartStore.totalItemsCount > 0" class="badge badge-secondary ml-2">
          {{ cartStore.totalItemsCount }}
        </div>
      </button>

      <div
        v-if="isCartOpen"
        class="card card-compact dropdown-content z-50 mt-3 w-96 bg-base-100 shadow-2xl border border-base-200"
      >
        <div class="card-body p-4">
          <div class="flex justify-between items-center px-2">
            <h3 class="text-lg font-bold">{{ cartStore.totalItemsCount }} Items</h3>
            <span
              v-if="cartStore.isLoading"
              class="loading loading-dots loading-sm text-primary"
            ></span>
          </div>

          <ul v-if="cartStore.items.length > 0" class="list max-h-96 overflow-y-auto mt-2">
            <li
              v-for="item in cartStore.items"
              :key="item.id"
              class="list-row items-center border-b border-base-200 last:border-0 px-2 py-3"
            >
              <div class="size-14 bg-base-200 mask mask-squircle shrink-0">
                <img
                  v-if="item.image_id"
                  :src="productImageUrl(item.image_id)"
                  class="object-cover size-full"
                  alt="Product"
                />
              </div>

              <div class="list-col-grow min-w-0">
                <div class="text-sm font-bold truncate">{{ item.name }}</div>
                <div class="flex items-center gap-2 mt-1">
                  <div class="join border border-base-300">
                    <button
                      class="btn btn-ghost btn-xs join-item px-1"
                      @click="handleUpdateQty(item.id, item.cart_qty, -1)"
                      :disabled="cartStore.isLoading"
                    >
                      -
                    </button>
                    <span class="px-2 text-xs flex items-center bg-base-200">{{
                      item.cart_qty
                    }}</span>
                    <button
                      class="btn btn-ghost btn-xs join-item px-1"
                      @click="handleUpdateQty(item.id, item.cart_qty, 1)"
                      :disabled="cartStore.isLoading"
                    >
                      +
                    </button>
                  </div>
                  <span class="text-xs opacity-60">× {{ item.price }} kr</span>
                </div>
              </div>

              <div class="list-col-wrap flex flex-col items-end gap-1">
                <span class="text-xs font-bold">{{ item.cart_qty * item.price }} kr</span>
                <button
                  class="btn btn-ghost btn-xs btn-circle text-error"
                  @click="handleRemove(item.id)"
                  :disabled="cartStore.isLoading"
                >
                  ✕
                </button>
              </div>
            </li>
          </ul>

          <div v-else-if="!cartStore.isLoading" class="py-10 text-center text-sm opacity-50">
            Your cart is empty
          </div>

          <div class="border-t border-base-200 pt-4 mt-2">
            <div class="flex justify-between items-center mb-4 px-2">
              <span class="text-sm opacity-70">Subtotal</span>
              <span class="text-xl font-black text-primary">{{ cartStore.cartTotal }} kr</span>
            </div>

            <div class="card-actions flex gap-2">
              <button
                class="btn btn-primary flex-1"
                :disabled="cartStore.items.length === 0 || cartStore.isLoading"
                @click="closeCart"
              >
                Checkout
              </button>

              <button
                class="btn btn-ghost btn-square text-error"
                @click="handleClearCart"
                :disabled="cartStore.items.length === 0 || cartStore.isLoading"
                title="Clear Cart"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="size-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            </div>

            <div v-if="cartStore.error" class="text-error text-[10px] mt-2 text-center">
              {{ cartStore.error }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
