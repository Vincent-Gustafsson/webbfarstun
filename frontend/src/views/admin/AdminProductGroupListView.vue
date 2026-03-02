<script setup lang="ts">
import AdminProductGroupList from '@/components/admin/AdminProductGroupList.vue'
</script>

<template>
  <main class="p-4 space-y-6">
    <AdminProductGroupList @cancel="$router.push('/')" />
  </main>
</template>
