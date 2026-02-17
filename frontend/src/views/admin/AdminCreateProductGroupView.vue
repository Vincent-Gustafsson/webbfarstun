<script setup lang="ts">
import AdminCreateProductGroupForm from '@/components/admin/AdminCreateProductGroupForm.vue'
import { useProductGroupStore } from '@/stores/admin/adminCreateProductGroup'

const productGroupStore = useProductGroupStore()

function clearError() {
  productGroupStore.error = null
  productGroupStore.fieldErrors = {}
}
</script>

<template>
  <main class="p-4 space-y-6">
    <AdminCreateProductGroupForm
      :submitting="productGroupStore.loading"
      :general-error="productGroupStore.error"
      :server-field-errors="productGroupStore.fieldErrors"
      @clear-error="clearError"
      @create="productGroupStore.create"
      @cancel="$router.push('/')"
    />
  </main>
</template>
