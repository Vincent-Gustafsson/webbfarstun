<script setup lang="ts">
import VariationOptionForm from '@/components/admin/AdminVariationOption.vue'
import { useVariationOptionStore } from '@/stores/admin/adminVariationOption'
const variationOptionStore = useVariationOptionStore()
</script>

<template>
  <main class="p-4">
    <VariationOptionForm
      :submitting="variationOptionStore.loading"
      :general-error="variationOptionStore.error"
      :server-field-errors="variationOptionStore.fieldErrors"
      @clear-error="variationOptionStore.error = null"
      @create="variationOptionStore.create"
      @cancel="$router.push('/')"
    />
  </main>
</template>
