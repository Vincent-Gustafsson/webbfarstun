<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCategoryStore } from '@/stores/admin/adminCategory'
import { useVariationStore } from '@/stores/admin/adminVariation'
import { useVariationOptionStore } from '@/stores/admin/adminVariationOption'

import AdminCategoryForm from '@/components/admin/AdminCategoryForm.vue'
import AdminCategoryVariationsEditor from '@/components/admin/AdminCategoryVariationsEditor.vue'

const route = useRoute()
const router = useRouter()

const categoryStore = useCategoryStore()
const variationStore = useVariationStore()
const optionStore = useVariationOptionStore()

const categoryId = computed(() => Number(route.params.category_id))
const category = computed(() => categoryStore.currentCategory)

function clearCategoryError() {
  categoryStore.error = null
  categoryStore.fieldErrors = {}
}

onMounted(async () => {
  const id = categoryId.value
  if (!Number.isFinite(id)) return

  await categoryStore.fetchById(id)

  await variationStore.fetchAll(true)
  await optionStore.fetchAll(true)
})
</script>

<template>
  <AdminCategoryForm
    mode="update"
    :category="category"
    :submitting="categoryStore.loading"
    :general-error="categoryStore.error"
    :server-field-errors="categoryStore.fieldErrors"
    @clear-error="clearCategoryError"
    @cancel="router.push('/admin/categories/list')"
    @update="(payload) => categoryStore.update(categoryId, payload)"
  />

  <AdminCategoryVariationsEditor v-if="category" :category-id="category.id" mode="update" />
</template>
