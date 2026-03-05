<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import HeroCarousel from '@/components/HeroCarousel.vue'
import ProductsListItem from '@/components/ProductsListItem.vue'
import { useProductStore } from '@/stores/products'

const productsStore = useProductStore()
const { products, loading, error } = storeToRefs(productsStore)

const latestProducts = computed(() => products.value.slice(-15).reverse())

onMounted(() => {
  productsStore.fetchAll()
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <HeroCarousel />

    <ul class="list bg-base-100 rounded-box shadow-md">
      <li class="p-4 pb-2 text-xs opacity-60 tracking-wide">
        Newest Products
        <span v-if="loading" class="ml-2 opacity-60">Laddar…</span>
      </li>

      <li v-if="error" class="p-4 text-sm text-error">
        {{ error }}
      </li>

      <li v-if="!loading && latestProducts.length === 0" class="p-4 text-sm opacity-70">
        Inga produkter hittades.
      </li>

      <ProductsListItem v-for="p in latestProducts" :key="p.id" :product="p" />
    </ul>
  </div>
</template>
