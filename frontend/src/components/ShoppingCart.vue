<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import { productImageUrl } from '@/services/products.ts'

const cartStore = useCartStore()
const isCartOpen = ref(false)

const toggleCart = () => (isCartOpen.value = !isCartOpen.value)
const closeCart = () => (isCartOpen.value = false)

onMounted(() => {
  cartStore.fetchCart()
})

// Logic to remove an item (assuming you'll add this to your store later)
const handleRemove = async (itemId: number) => {
  // await cartStore.removeItem(itemId)
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
      <button type="button" class="btn btn-primary relative z-50" @click="toggleCart">
        Cart
        <div v-if="cartStore.totalItemsCount > 0" class="badge badge-secondary ml-2">
          {{ cartStore.totalItemsCount }}
        </div>
      </button>

      <div
        v-if="isCartOpen"
        class="card card-compact dropdown-content z-50 mt-3 w-80 bg-base-100 shadow-2xl border border-base-200"
      >
        <div class="card-body p-4">
          <h3 class="text-lg font-bold px-2">{{ cartStore.totalItemsCount }} Items</h3>

          <ul v-if="cartStore.items.length > 0" class="list max-h-80 overflow-y-auto">
            <li
              v-for="item in cartStore.items"
              :key="item.id"
              class="list-row items-center border-b border-base-200 last:border-0 px-2 py-3"
            >
              <div class="size-12 bg-base-200 mask mask-squircle shrink-0">
                <img
                  v-if="item.image_id"
                  :src="productImageUrl(item.image_id)"
                  class="object-cover size-full"
                  alt="Product"
                />
              </div>

              <div class="list-col-grow min-w-0">
                <div class="text-sm font-bold truncate">{{ item.name }}</div>
                <div class="text-xs opacity-60">{{ item.cart_qty }} × {{ item.price }} kr</div>
              </div>

              <div class="list-col-wrap flex flex-col items-end gap-1">
                <span class="text-xs font-bold">{{ item.cart_qty * item.price }} kr</span>
                <button
                  class="btn btn-ghost btn-xs btn-circle text-error"
                  @click="handleRemove(item.id)"
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
                :disabled="cartStore.items.length === 0"
                @click="closeCart"
              >
                Checkout
              </button>

              <button
                class="btn btn-ghost btn-square text-error"
                @click="cartStore.clearCart"
                title="Clear Cart"
              >
                <svg
                  xmlns="http://www.w3.org/2000/vue"
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Optional: Slim custom scrollbar for the list */
.list::-webkit-scrollbar {
  width: 4px;
}
.list::-webkit-scrollbar-thumb {
  background: hsl(var(--bc) / 0.1);
  border-radius: 10px;
}
</style>
