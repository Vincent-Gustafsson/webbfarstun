<script setup lang="ts">
import ProductForm from '@/components/AdminCreateProduct.vue'
import { useProductStore } from '@/stores/adminCreateProduct'

const productStore = useProductStore()
</script>

<template>
  <main class="p-4">
    <ProductForm
      :submitting="productStore.loading"
      :general-error="productStore.error"
      :server-field-errors="productStore.fieldErrors"
      @clear-error="productStore.error"
      @create="productStore.create"
      @cancel="$router.push('/')"
    />
  </main>
</template>
D
