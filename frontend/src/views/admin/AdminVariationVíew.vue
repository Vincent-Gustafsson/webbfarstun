<script setup lang="ts">
import VariationForm from '@/components/admin/AdminVariation.vue'
import { useVariationStore } from '@/stores/admin/adminVariation'

const variationStore = useVariationStore()
</script>

<template>
  <main class="p-4">
    <VariationForm
      :submitting="variationStore.loading"
      :general-error="variationStore.error"
      :server-field-errors="variationStore.fieldErrors"
      @clear-error="variationStore.error = null"
      @create="variationStore.create"
      @cancel="$router.push('/')"
    />
  </main>
</template>
