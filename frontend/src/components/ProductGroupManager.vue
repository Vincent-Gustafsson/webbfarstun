<script setup lang="ts">
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useProductGroupStore } from '@/stores/productGroup'
import type { CategoryNode } from '@/types/category'

// 1. Props: Receives the context from HomeView
const props = defineProps<{
  selectedCategory: CategoryNode | null
}>()

// 2. Store Access
const pgStore = useProductGroupStore()
const { productGroups, loading } = storeToRefs(pgStore)

// 3. Local State
const newGroupName = ref('')

// 4. Computed: Filter global list by the selected category prop
const filteredGroups = computed(() => {
  if (!props.selectedCategory) return []
  // Requires 'category_id' in your ProductGroup interface!
  return productGroups.value.filter((pg) => pg.category_id === props.selectedCategory?.id)
})

// 5. Actions
const handleCreate = async () => {
  if (!newGroupName.value || !props.selectedCategory) return

  try {
    await pgStore.create({
      name: newGroupName.value,
      category_id: props.selectedCategory.id,
    })
    newGroupName.value = '' // Reset input
  } catch (e) {
    console.error(e)
  }
}
</script>

<template>
  <div class="h-full flex flex-col">
    <div
      v-if="!selectedCategory"
      class="flex flex-1 items-center justify-center bg-base-200 rounded-box border-2 border-dashed border-base-300"
    >
      <div class="text-center opacity-50">
        <span class="text-4xl block mb-2">👈</span>
        <p>Select a category to manage groups</p>
      </div>
    </div>

    <div v-else class="flex flex-col h-full gap-4">
      <div class="border-b border-base-300 pb-2">
        <div class="text-xs uppercase tracking-wide opacity-50">Managing Groups For</div>
        <div class="text-2xl font-bold text-primary">{{ selectedCategory.name }}</div>
      </div>

      <div class="flex gap-2">
        <input
          v-model="newGroupName"
          @keyup.enter="handleCreate"
          type="text"
          placeholder="New Group Name (e.g. 'Cotton T-Shirts')..."
          class="input input-bordered w-full"
        />
        <button @click="handleCreate" class="btn btn-primary" :disabled="loading || !newGroupName">
          Add
        </button>
      </div>

      <div class="bg-base-200 rounded-box flex-1 overflow-hidden relative">
        <div class="absolute inset-0 overflow-y-auto p-2">
          <table class="table table-zebra w-full" v-if="filteredGroups.length > 0">
            <thead>
              <tr>
                <th>ID</th>
                <th class="w-full">Name</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="group in filteredGroups" :key="group.id">
                <td class="opacity-50 text-xs">{{ group.id }}</td>
                <td class="font-medium">{{ group.name }}</td>
                <td>
                  <button
                    @click="pgStore.remove(group.id)"
                    class="btn btn-ghost btn-xs text-error"
                    title="Delete Group"
                  >
                    ✕
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-else class="text-center py-10 opacity-60">
            <p>No product groups yet.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
