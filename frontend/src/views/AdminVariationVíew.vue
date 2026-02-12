<script setup lang="ts">
import VariationForm from '@/components/AdminVariation.vue'
import { useVariationStore } from '@/stores/adminVariation'

const variationStore = useVariationStore()
</script>

<template>
  <main class="p-4">
    <VariationForm
      :submitting="variationStore.loading"
      :error="variationStore.error"
      @clear-error="variationStore.error = null"
      @create="variationStore.create"
      @cancel="$router.push('/')"
    />
  </main>
</template>
