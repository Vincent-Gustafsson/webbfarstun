<script setup lang="ts">
import ProductForm from '@/components/AdminCreateProduct.vue'
import { useProductStore } from '@/stores/adminCreateProduct'

const productStore = useProductStore()
</script>

<template>
  <main class="p-4">
    <ProductForm
      :submitting="productStore.loading"
      :error="productStore.error"
      @clear-error="productStore.error = null"
      @create="productStore.create"
      @cancel="$router.push('/')"
    />
  </main>
</template>
