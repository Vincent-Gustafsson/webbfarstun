<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useProductGroupStore } from '@/stores/admin/adminCreateProductGroup'
import { useCategoryStore } from '@/stores/admin/adminCategory'
const productGroupStore = useProductGroupStore()
const categoryStore = useCategoryStore()

const productGroups = computed(() => productGroupStore.productGroups)
const categories = computed(() => categoryStore.categories)
const loading = computed(() => productGroupStore.loading)
const error = computed(() => productGroupStore.error)

onMounted(async () => {
  await Promise.all([productGroupStore.fetchAll(), categoryStore.fetchAll()])
})

function onDelete(id: number, name?: string) {
  const ok = confirm(`Delete product group${name ? ` "${name}"` : ''}?`)
  if (!ok) return
  productGroupStore.remove(id)
}

const categoryNameById = computed<Record<number, string>>(() => {
  const map: Record<number, string> = {}
  for (const c of categories.value) map[c.id] = c.name
  return map
})
</script>

<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="error">{{ error }}</div>

  <ul v-else class="list bg-base-100 rounded-box shadow-md">
    <li class="list-row" v-for="pg in productGroups" :key="pg.id">
      <div>
        <div class="text-xs uppercase font-semibold opacity-75">
          {{ pg.name }}
        </div>
        <div class="text-xs opacity-50">
          <span class="font-semibold">Category:</span>
          {{ categoryNameById[pg.category_id] ?? 'Unknown' }}
        </div>
      </div>

      <div class="flex justify-end space-x-2">
        <button class="btn btn-soft btn-error" @click="onDelete(pg.id, pg.name)">Delete</button>

        <RouterLink
          class="btn btn-soft btn-warning"
          :to="{ name: 'admin-product-group-update', params: { product_group_id: pg.id } }"
        >
          Update
        </RouterLink>
      </div>
    </li>
  </ul>
</template>
