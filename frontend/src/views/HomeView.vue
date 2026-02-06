<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'

// Stores
import { useCategoryStore } from '@/stores/category'
import { useProductGroupStore } from '@/stores/productGroup'

// Components
import CategoryTree from '@/components/CategoryTree.vue'
import ProductGroupManager from '@/components/ProductGroupManager.vue'

// Types
import type { CategoryNode } from '@/types/category'

// 1. Setup Data
const categoryStore = useCategoryStore()
const pgStore = useProductGroupStore()
const { tree } = storeToRefs(categoryStore)

// 2. Selection State (Shared between Tree and Manager)
const selectedNode = ref<CategoryNode | null>(null)

// 3. Initial Load
onMounted(() => {
  categoryStore.fetchAll()
  pgStore.fetchAll()
})

// 4. Handlers
const onSelectCategory = (node: CategoryNode) => {
  selectedNode.value = node
}

const onCreateRoot = async () => {
  const name = prompt('Enter Root Category Name:')
  if (name) await categoryStore.create({ name })
}

// Passthrough: Tree requests creation of a subcategory
const onTreeCreate = async (payload: { name: string; parentId: number }) => {
  await categoryStore.create({
    name: payload.name,
    category_parent_id: payload.parentId,
  })
}
</script>

<template>
  <div class="h-screen flex flex-col bg-base-100 p-6 overflow-hidden">
    <header class="flex justify-between items-center mb-6 shrink-0">
      <h1 class="text-3xl font-bold">Shop Manager</h1>
    </header>

    <div class="flex flex-1 gap-6 overflow-hidden">
      <aside class="w-80 flex flex-col gap-2 shrink-0">
        <div class="flex justify-between items-center px-1">
          <h2 class="font-semibold opacity-70">Categories</h2>
          <button @click="onCreateRoot" class="btn btn-xs btn-outline">+ Root</button>
        </div>

        <div class="bg-base-200 rounded-box p-4 flex-1 overflow-y-auto">
          <ul class="menu w-full p-0">
            <CategoryTree
              :nodes="tree"
              @select="onSelectCategory"
              @remove="categoryStore.remove"
              @create="onTreeCreate"
            />
          </ul>
        </div>
      </aside>

      <main class="flex-1 min-w-0">
        <ProductGroupManager :selectedCategory="selectedNode" />
      </main>
    </div>
  </div>
</template>
