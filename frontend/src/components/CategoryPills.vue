<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useCategoryStore } from '@/stores/category'
import type { CategoryNode } from '@/types/category'

const store = useCategoryStore()

onMounted(() => {
  if (!store.tree.length) store.fetchAll()
})

const nodes = computed(() => store.tree)
const activeId = computed(() => store.activeCategoryId)

function findPath(tree: CategoryNode[], targetId: number | null): CategoryNode[] {
  if (targetId == null) return []
  for (const n of tree) {
    if (n.id === targetId) return [n]
    const childPath = findPath(n.children, targetId)
    if (childPath.length) return [n, ...childPath]
  }
  return []
}

const path = computed(() => findPath(nodes.value, activeId.value))
const activeNode = computed(() => (path.value.length ? path.value[path.value.length - 1] : null))

// Pills to show as “next step”: children of active node, otherwise top-level
const levelPills = computed(() => {
  const n = activeNode.value
  return n && n.children.length ? n.children : nodes.value
})

const toAll = computed(() => ({ name: 'categories', params: {} }))
const toCategory = (id: number) => ({ name: 'categories', params: { category_id: id } })
</script>

<template>
  <!-- DaisyUI breadcrumbs -->
  <div class="breadcrumbs text-sm">
    <ul>
      <li>
        <RouterLink :to="{ name: 'home' }" class="inline-flex items-center gap-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 512 512"
            class="w-4 h-4"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              d="M277.8 8.6c-12.3-11.4-31.3-11.4-43.5 0l-224 208c-9.6 9-12.8 22.9-8 35.1S18.8 272 32 272l16 0 0 176c0 35.3 28.7 64 64 64l288 0c35.3 0 64-28.7 64-64l0-176 16 0c13.2 0 25-8.1 29.8-20.3s1.6-26.2-8-35.1l-224-208zM240 320l32 0c26.5 0 48 21.5 48 48l0 96-128 0 0-96c0-26.5 21.5-48 48-48z"
            />
          </svg>
        </RouterLink>
      </li>

      <li v-for="n in path" :key="n.key">
        <RouterLink :to="toCategory(n.id)">
          {{ n.name }}
        </RouterLink>
      </li>
    </ul>
  </div>
</template>
