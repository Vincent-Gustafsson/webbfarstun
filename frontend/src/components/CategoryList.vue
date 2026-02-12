<script setup lang="ts">
import type { CategoryNode } from '@/types/category'

const props = defineProps<{
  nodes: CategoryNode[]
}>()
</script>

<template>
  <ul class="list">
    <router-link
      :to="{ name: 'categories', params: { category_id: node.id } }"
      v-for="node in props.nodes"
      :key="node.id"
      class="list-item"
    >
      {{ node.name }}
    </router-link>
  </ul>
</template>
