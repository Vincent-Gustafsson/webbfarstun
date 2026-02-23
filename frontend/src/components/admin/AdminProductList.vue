<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useProductStore } from '@/stores/admin/adminCreateProduct'

import { productImageUrl } from '@/services/products.ts'

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
  <div v-else class="list bg-base-100 rounded-box shadow-md">
    <div v-for="p in products" :key="p.id" class="card bg-base-100 w-96 shadow-sm">
      <figure>
        <img :src="productImageUrl(p.default_image)" alt="Shoes" />
      </figure>
      <div class="card-body">
        <h2 class="card-title">{{ p.name }}</h2>
        <p>{{ p.description }}</p>
        <p>{{ p.price }} kr</p>
        <p>{{ p.stock_qty }} st</p>
        <div class="card-actions justify-end">
          <div class="flex justify-end space-x-2">
            <button class="btn btn-soft btn-error">Delete</button>
            <button class="btn btn-soft btn-warning">
              <RouterLink
                v-if="p.id != null"
                :to="{ name: 'admin-product-update', params: { product_id: p.id } }"
              >
                Update
              </RouterLink>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
