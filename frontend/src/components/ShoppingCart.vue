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

const handleCheckout = async () => {
  await cartStore.checkout()
}

const getProductRoute = (productId: number) => ({
  name: 'productDetails',
  params: { id: productId },
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
  <div class="relative mr-2">
    <Transition name="fade">
      <div
        v-if="isCartOpen"
        @click="closeCart"
        class="fixed inset-0 z-40 bg-neutral/60 transition-all"
      ></div>
    </Transition>

    <div :class="['dropdown dropdown-end', { 'dropdown-open': isCartOpen }]">
      <div class="indicator">
        <span class="indicator-item badge badge-sm badge-secondary z-51">{{
          cartStore.totalItemsCount
        }}</span>
        <button
          type="button"
          class="btn btn-primary relative z-50"
          @click="toggleCart"
          :disabled="!users.isLoggedIn || (cartStore.isLoading && cartStore.items.length === 0)"
        >
          Cart
        </button>
      </div>

      <div
        v-if="isCartOpen"
        class="card card-compact dropdown-content z-50 mt-3 w-110 bg-base-100 shadow-2xl border border-base-200"
      >
        <div class="card-body p-4">
          <div class="flex justify-between items-center px-2">
            <h3 class="text-lg font-bold">{{ cartStore.totalItemsCount }} Items</h3>
            <span
              v-if="cartStore.isLoading"
              class="loading loading-dots loading-sm text-primary"
            ></span>
          </div>

          <ul
            v-if="cartStore.items.length > 0"
            class="max-h-96 overflow-y-auto flex flex-col w-full overscroll-contain"
          >
            <li
              v-for="item in cartStore.items"
              :key="item.id"
              class="flex items-start gap-4 py-4 px-2 border-b border-base-200 last:border-0 hover:bg-base-200/20 transition-colors"
            >
              <RouterLink
                :to="getProductRoute(item.product_id)"
                class="shrink-0 hover:opacity-80 transition-opacity"
                @click="closeCart"
              >
                <div
                  class="w-25 h-15 shrink-0 bg-base-200 rounded-md overflow-hidden border border-base-200 flex items-center justify-center"
                >
                  <img
                    v-if="item.image_id"
                    :src="productImageUrl(item.image_id)"
                    class="object-cover w-full h-full"
                    :alt="item.name"
                  />
                </div>
              </RouterLink>

              <div class="flex-1 min-w-0">
                <div class="flex-1 min-w-0">
                  <RouterLink
                    :to="getProductRoute(item.product_id)"
                    class="text-sm font-bold truncate text-base-content block hover:text-primary transition-colors"
                    @click="closeCart"
                  >
                    {{ item.name }}
                  </RouterLink>

                  <div class="text-xs text-base-content/60 mt-0.5">{{ item.price }} kr / st</div>
                </div>

                <div class="join border border-base-300 mt-2 bg-base-100">
                  <button
                    class="btn btn-xs join-item border-none hover:bg-base-300"
                    @click="handleUpdateQty(item.id, item.cart_qty, -1)"
                    :disabled="cartStore.isLoading"
                    aria-label="Decrease quantity"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      class="size-3"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2.5"
                        d="M20 12H4"
                      />
                    </svg>
                  </button>

                  <div
                    class="join-item flex items-center justify-center px-3 text-xs font-semibold border-none min-w-[2.5rem]"
                  >
                    {{ item.cart_qty }}
                  </div>

                  <button
                    class="btn btn-xs join-item border-none hover:bg-base-300"
                    @click="handleUpdateQty(item.id, item.cart_qty, 1)"
                    :disabled="cartStore.isLoading"
                    aria-label="Increase quantity"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      class="size-3"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2.5"
                        d="M12 4v16m8-8H4"
                      />
                    </svg>
                  </button>
                </div>
              </div>

              <div class="flex flex-col items-end justify-between self-stretch shrink-0 ml-2">
                <span class="text-sm font-black">{{ item.cart_qty * item.price }} kr</span>

                <button
                  class="btn btn-ghost btn-xs text-base-content/40 hover:text-error hover:bg-error/10"
                  @click="handleRemove(item.id)"
                  :disabled="cartStore.isLoading"
                  title="Remove item"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="size-4"
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
                @click="handleCheckout"
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
