<script setup lang="ts">
import AdminProductList from '@/components/admin/AdminProductList.vue'
</script>

<template>
  <main class="p-4 space-y-6">
    <AdminProductList @cancel="$router.push('/')" />
  </main>
</template>
