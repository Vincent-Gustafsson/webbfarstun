<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useCategoryStore } from '@/stores/admin/adminCategory'

const categoryStore = useCategoryStore()

const categories = computed(() => categoryStore.categories)
const loading = computed(() => categoryStore.loading)
const error = computed(() => categoryStore.error)

onMounted(async () => {
  await categoryStore.fetchAll()
})
</script>

<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="error">{{ error }}</div>
  <ul v-else class="list bg-base-100 rounded-box shadow-md">
    <li class="list-row" v-for="c in categories" :key="c.id">
      <div>
        <div class="text-xs uppercase font-semibold opacity-60">{{ c.name }}</div>
      </div>
      <p class="list-col-wrap text-xs">
        <span class="text-xs uppercase font-semibold">Description:</span>
        {{ c.description }}
      </p>
      <div class="list-col-wrap text-xs">
        <span class="text-xs uppercase font-semibold">Is_container: </span>
        <span
          :class="c.is_container ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'"
        >
          {{ c.is_container ? 'Yes' : 'No' }}
        </span>
      </div>

      <div class="flex justify-end space-x-2">
        <button class="btn btn-soft btn-error">Delete</button>
        <button class="btn btn-soft btn-warning">
          <RouterLink :to="{ name: 'admin-category-update', params: { category_id: c.id } }">
            Update
          </RouterLink>
        </button>
      </div>
    </li>
  </ul>
</template>
