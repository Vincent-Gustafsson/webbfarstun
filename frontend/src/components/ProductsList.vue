<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useCategoryStore } from '@/stores/category'
import { useProductStore } from '@/stores/products'
import ProductsListItem from '@/components/ProductsListItem.vue'

const categoryStore = useCategoryStore()
const productStore = useProductStore()

const { activeCategoryId } = storeToRefs(categoryStore)
const { products, loading, error } = storeToRefs(productStore)

const count = computed(() => products.value.length)

async function loadProducts(categoryId: number | null) {
  const params = categoryId != null ? { category_id: categoryId } : {}
  await productStore.fetchAll(params)
}

onMounted(async () => {
  await categoryStore.fetchAll()
  await loadProducts(activeCategoryId.value)
})

watch(
  activeCategoryId,
  async (newId) => {
    await loadProducts(newId)
  },
  { immediate: false },
)
</script>

<template>
  <ul class="list bg-base-100 rounded-box shadow-md">
    <li class="p-4 pb-2 text-xs opacity-60 tracking-wide">
      Visar {{ count }} produkter
      <span v-if="loading" class="ml-2 opacity-60">Laddar…</span>
    </li>

    <li v-if="error" class="p-4 text-sm text-error">
      {{ error }}
    </li>

    <li v-if="!loading && products.length === 0" class="p-4 text-sm opacity-70">
      Inga produkter hittades.
    </li>

    <ProductsListItem v-for="p in products" :key="p.id" :product="p" />
  </ul>
</template>
