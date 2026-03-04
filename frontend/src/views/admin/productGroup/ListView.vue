<script setup lang="ts">
import AdminProductGroupList from '@/components/admin/productGroup/List.vue'
</script>

<template>
  <main class="p-4 space-y-6">
    <AdminProductGroupList @cancel="$router.push('/')" />
  </main>
</template>
