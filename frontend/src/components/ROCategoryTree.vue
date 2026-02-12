<script setup lang="ts">
import { computed } from 'vue'
import type { CategoryNode } from '@/types/category'

defineOptions({ name: 'ROCategoryTree' })

const props = withDefaults(
  defineProps<{
    nodes: CategoryNode[]
    selectedId?: number | null
    openIds?: number[] // ids that should be expanded (typically the breadcrumb path)
    defaultOpen?: boolean
    root?: boolean
  }>(),
  {
    selectedId: null,
    openIds: () => [],
    defaultOpen: false,
    root: true,
  },
)

const emit = defineEmits<{
  (e: 'select', node: CategoryNode): void
}>()

const openSet = computed(() => new Set(props.openIds))
const isOpen = (id: number) => props.defaultOpen || openSet.value.has(id)
</script>

<template>
  <ul :class="props.root ? 'menu menu-sm' : 'menu menu-sm pl-4'">
    <li v-for="node in props.nodes" :key="node.id">
      <!-- Branch -->
      <details v-if="node.children?.length" :open="isOpen(node.id)">
        <summary
          class="gap-2"
          :class="{
            active: props.selectedId === node.id,
            'font-semibold': props.selectedId === node.id,
          }"
          @click="emit('select', node)"
        >
          {{ node.name }}
        </summary>

        <ROCategoryTree
          :nodes="node.children"
          :selected-id="props.selectedId"
          :open-ids="props.openIds"
          :default-open="props.defaultOpen"
          :root="false"
          @select="emit('select', $event)"
        />
      </details>

      <!-- Leaf -->
      <a
        v-else
        :class="{
          active: props.selectedId === node.id,
          'font-semibold': props.selectedId === node.id,
        }"
        @click.prevent="emit('select', node)"
      >
        {{ node.name }}
      </a>
    </li>
  </ul>
</template>
