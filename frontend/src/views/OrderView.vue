<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useOrderStore } from '@/stores/order'
import OrderCard from '@/components/Order.vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import type { Order } from '@/types/order'

const orderStore = useOrderStore()
const userStore = useUserStore()
const router = useRouter()

onMounted(async () => {
  if (!userStore.me) {
    await userStore.fetchMe()
  }

  if (userStore.me && userStore.me.id) {
    await orderStore.loadOrders(userStore.me.id)
  } else {
    console.error('User is not authenticated. Cannot fetch orders.')
    router.push('/account/login')
  }
})

// Gruppera ordrar baserat på order_nr
const groupedOrders = computed(() => {
  const groups: Record<
    string,
    {
      order_nr: number
      purchased_at: string
      total_amount: number
      items: Order[]
    }
  > = {}

  orderStore.orders.forEach((order) => {
    const key = String(order.order_nr)
    let group = groups[key]

    if (!group) {
      group = {
        order_nr: order.order_nr,
        purchased_at: order.purchased_at,
        total_amount: 0,
        items: [],
      }
      groups[key] = group
    }

    group.items.push(order)
    group.total_amount += order.line_total
  })

  // Returnera som en array och sortera så att nyaste beställningen hamnar först
  return Object.values(groups).sort(
    (a, b) => new Date(b.purchased_at).getTime() - new Date(a.purchased_at).getTime(),
  )
})
</script>

<template>
  <div class="max-w-5xl mx-auto p-6 bg-base-200 min-h-screen">
    <div class="mb-4 text-sm text-base-content/70">
      Visar {{ groupedOrders.length }} beställningar ({{ orderStore.orders.length }} produkter)
    </div>

    <div
      v-if="orderStore.isLoading"
      class="p-8 text-center text-base-content/50 bg-base-100 rounded-box shadow-sm"
    >
      <span class="loading loading-spinner loading-md text-primary"></span>
    </div>

    <div
      v-else-if="groupedOrders.length === 0"
      class="p-12 text-center text-base-content/60 bg-base-100 rounded-box shadow-sm"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-12 w-12 mx-auto mb-4 opacity-50"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
        />
      </svg>
      <p class="text-lg font-medium">Inga beställningar gjorda</p>
      <p class="text-sm mt-1">När du har lagt en beställning kommer den att visas här.</p>
    </div>

    <div v-else class="flex flex-col gap-6">
      <OrderCard v-for="group in groupedOrders" :key="group.order_nr" :orderGroup="group" />
    </div>
  </div>
</template>
