<script setup lang="ts">
import { computed } from 'vue'
import { useCategoryStore } from '@/stores/admin/adminCategory'
import { useVariationStore } from '@/stores/admin/adminVariation'
import { useVariationOptionStore } from '@/stores/admin/adminVariationOption'

import AdminCategoryForm from '@/components/admin/AdminCategoryForm.vue'
import AdminCategoryVariationsEditor from '@/components/admin/AdminCategoryVariationsEditor.vue'


const categoryStore = useCategoryStore()
const variationStore = useVariationStore()
const optionStore = useVariationOptionStore()


const category = computed(() => categoryStore.currentCategory)
const loading = computed(
  () => categoryStore.loading || variationStore.loading || optionStore.loading,
)
</script>

<template>
  <div>
    <div v-if="loading">Loading...</div>

    <div v-else>
      <AdminCategoryForm mode="update" :category="category" />

      <AdminCategoryVariationsEditor v-if="category" :categoryId="category.id" mode="update" />
    </div>
  </div>
</template>
