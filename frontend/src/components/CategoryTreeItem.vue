<script setup lang="ts">
import { computed } from 'vue'
import type { CategoryNode } from '@/types/category'

defineOptions({ name: 'CategoryTreeItem' })

const props = defineProps<{
  node: CategoryNode
  activeId: number | null
}>()

const isActive = computed(() => props.activeId === props.node.id)

function containsActive(node: CategoryNode, id: number | null): boolean {
  if (id == null) return false
  if (node.id === id) return true
  return node.children.some((c) => containsActive(c, id))
}

const shouldOpen = computed(() => containsActive(props.node, props.activeId))

const toCategory = computed(() => ({
  name: 'categories',
  params: { category_id: props.node.id },
}))
</script>

<template>
  <li>
    <details v-if="node.children.length" :open="shouldOpen">
      <summary class="gap-2" :class="{ active: isActive }">
        <RouterLink :to="toCategory" class="flex-1" @click.stop>
          {{ node.name }}
        </RouterLink>
      </summary>

      <ul>
        <CategoryTreeItem
          v-for="child in node.children"
          :key="child.key"
          :node="child"
          :active-id="activeId"
        />
      </ul>
    </details>

    <RouterLink v-else :to="toCategory" :class="{ active: isActive }">
      {{ node.name }}
    </RouterLink>
  </li>
</template>
