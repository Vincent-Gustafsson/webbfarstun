<script setup lang="ts">
import { computed } from 'vue'
import { useProductStore } from '@/stores/admin/adminCreateProduct'

import AdminCreateProductForm from '@/components/admin/AdminCreateProductForm.vue'


const productStore = useProductStore()


const product = computed(() => productStore.current)
const loading = computed(() => productStore.loading)
</script>

<template>
  <div>
    <div v-if="loading">Loading...</div>

    <div v-else>
      <AdminCreateProductForm mode="update" :product="product" />
    </div>
  </div>
</template>
