<script setup lang="ts">
import { ref, nextTick } from 'vue'
import type { CategoryNode } from '@/types/category'

// 1. Props
defineProps<{
  nodes: CategoryNode[]
}>()

// 2. Emits (added 'create')
const emit = defineEmits<{
  (e: 'select', node: CategoryNode): void
  (e: 'remove', id: number): void
  (e: 'create', payload: { name: string; parentId: number }): void
}>()

// 3. Local State for Inline Editing
const addingNodeId = ref<number | null>(null)
const newCategoryName = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

// Start adding: Show input and focus it
const startAdding = async (id: number) => {
  addingNodeId.value = id
  newCategoryName.value = ''
  await nextTick()
  inputRef.value?.focus()
}

// Cancel adding
const cancelAdding = () => {
  addingNodeId.value = null
  newCategoryName.value = ''
}

// Confirm adding
const confirmAdd = (parentId: number) => {
  if (!newCategoryName.value.trim()) return
  emit('create', { name: newCategoryName.value, parentId })
  addingNodeId.value = null // Close input
}
</script>

<template>
  <li v-for="node in nodes" :key="node.id">
    <details v-if="(node.children && node.children.length) || addingNodeId === node.id" open>
      <summary class="group justify-between">
        <span @click="emit('select', node)" class="cursor-pointer">{{ node.name }}</span>

        <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            @click.stop="startAdding(node.id)"
            class="btn btn-ghost btn-xs text-primary"
            title="Add Subcategory"
          >
            +
          </button>
          <button
            @click.stop="emit('remove', node.id)"
            class="btn btn-ghost btn-xs text-error"
            title="Delete Category"
          >
            ✕
          </button>
        </div>
      </summary>

      <ul>
        <CategoryTree
          v-if="node.children && node.children.length"
          :nodes="node.children"
          @select="emit('select', $event)"
          @remove="emit('remove', $event)"
          @create="emit('create', $event)"
        />

        <li v-if="addingNodeId === node.id">
          <div class="flex items-center gap-2 p-2 bg-base-200 rounded">
            <input
              ref="inputRef"
              v-model="newCategoryName"
              @keydown.enter="confirmAdd(node.id)"
              @keydown.esc="cancelAdding"
              type="text"
              class="input input-bordered input-xs w-full"
              placeholder="Name..."
            />
            <button @click="confirmAdd(node.id)" class="btn btn-xs btn-primary">✓</button>
            <button @click="cancelAdding" class="btn btn-xs btn-ghost">✕</button>
          </div>
        </li>
      </ul>
    </details>

    <a v-else class="group justify-between">
      <span @click="emit('select', node)">{{ node.name }}</span>

      <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button @click.stop="startAdding(node.id)" class="btn btn-ghost btn-xs text-primary">
          +
        </button>
        <button @click.stop="emit('remove', node.id)" class="btn btn-ghost btn-xs text-error">
          ✕
        </button>
      </div>
    </a>
  </li>
</template>
