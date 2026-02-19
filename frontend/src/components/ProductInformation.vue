<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useProductStore } from '@/stores/products.ts'

import StarRating from '@/components/StarRating.vue'

const productStore = useProductStore()
const { activeProduct } = storeToRefs(productStore)
</script>

<template>
  <div class="w-full card bg-base-100 shadow p-4">
    <template v-if="activeProduct">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-2xl">{{ activeProduct.name }}</h2>
          <p class="text-xs">{{ activeProduct.sku }}</p>
        </div>

        <div>
          <div class="tooltip" data-tip="3.2">
            <StarRating :model-value="3.2" size-class="rating-xs" bg-class="bg-accent" />
          </div>
          <p class="text-xs text-end">0 reviews</p>
        </div>
      </div>

      <div class="divider"></div>

      <div class="flex">
        <p class="flex-1">{{ activeProduct.description }}</p>

        <div class="carousel w-full h-100 flex-2">
          <div id="slide1" class="carousel-item relative w-full">
            <img src="https://dev.webbfarstun.shop/api/product-images/8/file" class="w-full" />
            <div
              class="absolute left-5 right-5 top-1/2 flex -translate-y-1/2 transform justify-between"
            >
              <a href="#slide4" class="btn btn-circle">❮</a>
              <a href="#slide2" class="btn btn-circle">❯</a>
            </div>
          </div>
          <div id="slide2" class="carousel-item relative w-full">
            <img
              src="https://img.daisyui.com/images/stock/photo-1609621838510-5ad474b7d25d.webp"
              class="w-full"
            />
            <div
              class="absolute left-5 right-5 top-1/2 flex -translate-y-1/2 transform justify-between"
            >
              <a href="#slide1" class="btn btn-circle">❮</a>
              <a href="#slide3" class="btn btn-circle">❯</a>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
