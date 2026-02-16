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
    if (v == null) return

    const id = Number(v)
    if (!Number.isFinite(id)) return

    store.setActiveCategory(id)
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
