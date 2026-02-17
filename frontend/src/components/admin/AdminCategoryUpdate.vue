<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCategoryStore } from '@/stores/admin/adminCategory'
import { useVariationStore } from '@/stores/admin/adminVariation'
import { useVariationOptionStore } from '@/stores/admin/adminVariationOption'

import AdminCategoryForm from '@/components/admin/AdminCategoryForm.vue'
import AdminCategoryVariationsEditor from '@/components/admin/AdminCategoryVariationsEditor.vue'

const route = useRoute()
const categoryStore = useCategoryStore()
const variationStore = useVariationStore()
const optionStore = useVariationOptionStore()

const categoryId = computed(() => Number(route.params.category_id))

const category = computed(() => categoryStore.currentCategory)
const loading = computed(
  () => categoryStore.loading || variationStore.loading || optionStore.loading,
)

onMounted(async () => {
  const id = categoryId.value
  if (!Number.isFinite(id)) return

  await categoryStore.fetchById(id)

  // load all variations/options (since your APIs are "getAll" currently)
  await variationStore.fetchAll()
  await optionStore.fetchAll()
})
</script>

<template>
  <div v-if="loading">Loading...</div>

  <div v-else>
    <!-- reuse same form, but in "edit mode" -->
    <AdminCategoryForm mode="update" :category="category" />

    <AdminCategoryVariationsEditor v-if="category" :categoryId="category.id" mode="update" />
  </div>
</template>
