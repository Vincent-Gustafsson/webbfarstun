<script setup lang="ts">
import AdminProductGroupForm from '@/components/admin/AdminCreateProductGroupForm.vue'
import AdminProductGroupAddVariations from '@/components/admin/AdminCreateProductGroupAddVariations.vue'
import { useProductGroupStore } from '@/stores/admin/adminCreateProductGroup'

const productGroupStore = useProductGroupStore()

function clearProductGroupError() {
  productGroupStore.error = null
  productGroupStore.fieldErrors = {}
}
</script>

<template>
  <main class="p-4 space-y-6">
    <AdminProductGroupForm
      :submitting="productGroupStore.loading"
      :general-error="productGroupStore.error"
      :server-field-errors="productGroupStore.fieldErrors"
      :created-product-group-id="productGroupStore.createdId"
      @clear-error="clearProductGroupError"
      @create="productGroupStore.create"
      @cancel="$router.push('/')"
    />

    <AdminProductGroupAddVariations :product-group-id="productGroupStore.createdId" />
  </main>
</template>
