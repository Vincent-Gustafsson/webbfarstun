<script setup lang="ts">
import { computed, onMounted, onActivated, ref } from 'vue'
import { useProductStore } from '@/stores/admin/product'
import { productImageUrl } from '@/services/products.ts'

const productStore = useProductStore()

const products = computed(() => productStore.products)
const loading = computed(() => productStore.loading)
const error = computed(() => productStore.error)

const deletingId = ref<number | null>(null)

async function load() {
  await productStore.fetchAll(true)
}

async function onDelete(p: { id: number; name: string }) {
  if (!p.id) return

  deletingId.value = p.id
  try {
    await productStore.remove(p.id)
  } finally {
    deletingId.value = null
  }
}

onMounted(load)
onActivated(load)
</script>

<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="error">{{ error }}</div>
  <div v-else class="list bg-base-100 rounded-box shadow-md">
    <div v-for="p in products" :key="p.id" class="card bg-base-100 w-96 shadow-sm">
      <figure>
        <img
          v-if="productImageUrl(p.default_image)"
          :src="productImageUrl(p.default_image)!"
          alt=""
        />
        <div v-else class="h-48 w-full bg-base-200 rounded"></div>
      </figure>
      <div class="card-body">
        <h2 class="card-title">{{ p.name }}</h2>
        <p>{{ p.description }}</p>
        <p>{{ p.price }} kr</p>
        <p>{{ p.stock_qty }} st</p>
        <div class="card-actions justify-end">
          <div class="flex justify-end space-x-2">
            <button
              class="btn btn-soft btn-error"
              :disabled="deletingId === p.id"
              @click="onDelete({ id: p.id!, name: p.name })"
            >
              {{ deletingId === p.id ? 'Deleting...' : 'Delete' }}
            </button>
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
