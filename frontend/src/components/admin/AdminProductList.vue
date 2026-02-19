<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useProductStore } from '@/stores/admin/adminCreateProduct'

const productStore = useProductStore()

const products = computed(() => productStore.products)
const loading = computed(() => productStore.loading)
const error = computed(() => productStore.error)

onMounted(async () => {
  await productStore.fetchAll()
})
</script>

<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="error">{{ error }}</div>
  <ul v-else class="list bg-base-100 rounded-box shadow-md">
    <li class="list-row" v-for="p in products" :key="p.id">
      <div>
        <div class="text-xs uppercase font-semibold opacity-60">{{ p.name }}</div>
      </div>
      <p class="list-col-wrap text-xs">
        <span class="text-xs uppercase font-semibold">Description:</span>
        {{ p.description }}
      </p>
      <div class="flex justify-end space-x-2">
        <button class="btn btn-soft btn-error">Delete</button>
        <button class="btn btn-soft btn-warning">
          <RouterLink :to="{ name: 'admin-product-update', params: { product_id: p.id } }">
            Update
          </RouterLink>
        </button>
      </div>
    </li>
  </ul>
</template>
