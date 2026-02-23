<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useProductStore } from '@/stores/products.ts'
import { productImageUrl } from '@/services/products.ts'
import StarRating from '@/components/StarRating.vue'

const productStore = useProductStore()
const { activeProduct } = storeToRefs(productStore)

// If your backend field is `product_images`, change `.images` -> `.product_images`
const imagesSorted = computed(() => {
  const imgs = activeProduct.value?.images ?? []
  return [...imgs].sort((a, b) => Number(b.is_default) - Number(a.is_default))
})

const slideId = (idx: number) => `slide${idx + 1}`
const prevIndex = (idx: number) =>
  imagesSorted.value.length ? (idx - 1 + imagesSorted.value.length) % imagesSorted.value.length : 0
const nextIndex = (idx: number) =>
  imagesSorted.value.length ? (idx + 1) % imagesSorted.value.length : 0
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

      <div class="flex gap-4">
        <p class="flex-1 text-sm">{{ activeProduct.description }}</p>

        <div class="carousel w-full flex-2 h-72 lg:h-96">
          <div
            v-for="(img, idx) in imagesSorted"
            :key="img.id"
            :id="slideId(idx)"
            class="carousel-item relative w-full flex items-center justify-center"
          >
            <img :src="productImageUrl(img.id)" class="max-h-48 max-w-[70%] object-contain" />

            <div
              class="absolute left-5 right-5 top-1/2 flex -translate-y-1/2 transform justify-between"
            >
              <a :href="`#${slideId(prevIndex(idx))}`" class="btn btn-circle">❮</a>
              <a :href="`#${slideId(nextIndex(idx))}`" class="btn btn-circle">❯</a>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
