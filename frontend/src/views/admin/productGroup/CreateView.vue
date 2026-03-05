<script setup lang="ts">
import AdminCreateProductGroupForm from '@/components/admin/productGroup/Form.vue'
import { useProductGroupStore } from '@/stores/admin/productGroup'

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
      @cancel="$router.push('/admin')"
    />
  </main>
</template>
