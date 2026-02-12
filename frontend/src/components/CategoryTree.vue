<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useCategoryStore } from '@/stores/category'
import CategoryTreeItem from './CategoryTreeItem.vue'

const store = useCategoryStore()
const route = useRoute()

watch(
  () => route.params.category_id,
  (v) => {
    const id = v != null ? Number(v) : null
    store.setActiveCategory(Number.isFinite(id as number) ? (id as number) : null)
  },
  { immediate: true },
)

const nodes = computed(() => store.tree)
const activeId = computed(() => store.activeCategoryId)
</script>

<template>
  <ul class="menu bg-base-100 rounded-box p-2">
    <CategoryTreeItem v-for="n in nodes" :key="n.key" :node="n" :active-id="activeId" />
  </ul>
</template>
