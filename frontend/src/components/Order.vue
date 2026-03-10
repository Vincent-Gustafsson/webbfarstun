<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Order } from '@/types/order'
import { productImageUrl } from '@/services/products.ts'

const props = defineProps<{
  orderGroup: {
    order_nr: string | number
    purchased_at: string
    total_amount: number
    items: Order[]
  }
}>()

const brokenImages = ref(new Set<string | number>())

function handleImageError(itemId: string | number) {
  brokenImages.value.add(itemId)
}

const formattedDate = computed(() => {
  if (!props.orderGroup.purchased_at) return 'Okänt datum'

  let dateString = props.orderGroup.purchased_at
  if (!dateString.endsWith('Z')) {
    dateString += 'Z'
  }

  const date = new Date(dateString)

  return new Intl.DateTimeFormat('sv-SE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
})
</script>

<template>
  <div
    class="bg-base-100 border border-base-300 rounded-box shadow-sm overflow-hidden flex flex-col w-full"
  >
    <div
      class="bg-base-200/50 p-4 border-b border-base-300 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
    >
      <div>
        <div class="flex items-center gap-2">
          <span class="font-bold text-lg">Order #{{ orderGroup.order_nr }}</span>
          <span class="w-2 h-2 rounded-full bg-success"></span>
        </div>
        <div class="text-sm text-base-content/70 mt-1">Beställd: {{ formattedDate }}</div>
      </div>
      <div class="text-right w-full sm:w-auto">
        <div class="text-sm text-base-content/70">Totalsumma</div>
        <div class="font-bold text-lg">{{ orderGroup.total_amount }} kr</div>
      </div>
    </div>

    <div class="flex flex-col">
      <div
        v-for="item in orderGroup.items"
        :key="item.id"
        class="flex flex-col sm:flex-row items-center justify-between p-4 border-b border-base-200 last:border-b-0 hover:bg-base-50 transition-colors w-full"
      >
        <div class="flex items-center gap-6 w-full sm:w-auto">
          <div
            v-if="!item.default_image || brokenImages.has(item.id)"
            class="w-24 h-24 bg-base-300 rounded-md shrink-0"
          ></div>

          <img
            v-else
            :src="productImageUrl(item.default_image)"
            :alt="item.product_name"
            @error="handleImageError(item.id)"
            class="w-24 h-24 object-contain shrink-0"
          />
          <div class="flex flex-col">
            <h3 class="font-bold text-base-content text-[15px]">{{ item.product_name }}</h3>
          </div>
        </div>

        <div
          class="flex items-center gap-6 mt-4 sm:mt-0 w-full sm:w-auto justify-between sm:justify-end"
        >
          <span class="text-base-content font-medium whitespace-nowrap">
            {{ item.qty }} st x {{ item.unit_price }} kr = {{ item.line_total }} kr
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
