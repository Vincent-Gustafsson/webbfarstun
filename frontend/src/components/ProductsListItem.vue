<script setup lang="ts">
import type { ProductListItem } from '@/types/product'
import { productImageUrl } from '@/services/products.ts'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import StarRating from '@/components/StarRating.vue'

const props = defineProps<{
  product: ProductListItem
}>()

const router = useRouter()

// Adjust these to match your actual route + param (id/slug/etc)
const productTo = computed(() => ({
  name: 'productDetails',
  params: { id: props.product.id },
}))

function goToDetails() {
  router.push(productTo.value)
}
</script>

<template>
  <li
    class="list-row flex items-center justify-between gap-4 px-4 py-3 border-b border-base-200 cursor-pointer hover:bg-base-200/40 focus:outline-none focus-visible:ring focus-visible:ring-primary/40"
    role="link"
    tabindex="0"
    @click="goToDetails"
    @keydown.enter.prevent="goToDetails"
    @keydown.space.prevent="goToDetails"
  >
    <div class="flex">
      <img :src="productImageUrl(product.default_image)" class="h-15 w-25" alt="" />

      <div class="ml-5">
        <!-- clickable + hoverable name -->
        <RouterLink :to="productTo" class="font-bold truncate link link-hover" @click.stop>
          {{ product.name }}
        </RouterLink>

        <div class="flex justify-center items-center gap-1">
          <div
            class="w-2 h-2 rounded-full"
            :class="product.stock_qty > 0 ? 'bg-success' : 'bg-error'"
          ></div>
          {{ product.stock_qty }} st
          <div class="tooltip" :data-tip="product.review_score">
            <StarRating
              :model-value="product.review_score"
              size-class="rating-xs"
              bg-class="bg-accent"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="flex items-center gap-4">
      <div class="font-semibold">{{ product.price }} kr</div>

      <button class="btn btn-secondary" type="button" @click.stop>
        <svg xmlns="http://www.w3.org/2000/svg" fill="white" class="size-5" viewBox="0 0 640 512">
          <path
            d="M24-16C10.7-16 0-5.3 0 8S10.7 32 24 32l45.3 0c3.9 0 7.2 2.8 7.9 6.6l52.1 286.3c6.2 34.2 36 59.1 70.8 59.1L456 384c13.3 0 24-10.7 24-24s-10.7-24-24-24l-255.9 0c-11.6 0-21.5-8.3-23.6-19.7l-5.1-28.3 303.6 0c30.8 0 57.2-21.9 62.9-52.2L568.9 69.9C572.6 50.2 557.5 32 537.4 32l-412.7 0-.4-2c-4.8-26.6-28-46-55.1-46L24-16zM208 512a48 48 0 1 0 0-96 48 48 0 1 0 0 96zm224 0a48 48 0 1 0 0-96 48 48 0 1 0 0 96z"
          />
        </svg>
        Add to cart
      </button>
    </div>
  </li>
</template>
