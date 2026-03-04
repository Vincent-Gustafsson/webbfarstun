<script setup lang="ts">
import AdminCategoryList from '@/components/admin/category/List.vue'
</script>

<template>
  <main class="p-4 space-y-6">
    <AdminCategoryList @cancel="$router.push('/')" />
  </main>
</template>
