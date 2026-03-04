<script setup lang="ts">
import AdminCategoryForm from '@/components/admin/category/Form.vue'
import CategoryVariationsEditor from '@/components/admin/category/CreateVariations.vue'
import { useCategoryStore } from '@/stores/admin/category'

const categoryStore = useCategoryStore()

function clearCategoryError() {
  categoryStore.error = null
  categoryStore.fieldErrors = {}
}
</script>

<template>
  <main class="p-4 space-y-6">
    <AdminCategoryForm
      :submitting="categoryStore.loading"
      :general-error="categoryStore.error"
      :server-field-errors="categoryStore.fieldErrors"
      :created-category-id="categoryStore.createdId"
      @clear-error="clearCategoryError"
      @create="categoryStore.create"
      @cancel="$router.push('/')"
    />

    <CategoryVariationsEditor :category-id="categoryStore.createdId" />
  </main>
</template>
