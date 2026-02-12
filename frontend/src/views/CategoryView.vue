<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useCategoryStore } from '@/stores/category'

const route = useRoute()
const categoryStore = useCategoryStore()

const categoryId = computed(() => Number(route.params.category_id))
const category = computed(() => categoryStore.getById(categoryId.value))

const subcategories = computed(() =>
  categoryStore.categories
    .filter((c) => c.category_parent_id === categoryId.value)
    .sort((a, b) => a.name.localeCompare(b.name)),
)

async function ensureLoaded(id: number) {
  // fetchAll gives you the children (and is cached by your store anyway)
  await categoryStore.fetchAll()
  // fetchOne ensures the current category exists even if backend list is partial
  await categoryStore.fetchOne(id)
}

onMounted(() => ensureLoaded(categoryId.value))
watch(categoryId, (id) => ensureLoaded(id))
</script>

<template>
  <div v-if="category" class="card bg-base-100 shadow">
    <div class="card-body md:flex md:flex-row md:items-stretch md:gap-6">
      <!-- Left: title + description -->
      <div class="md:w-1/2">
        <h1 class="card-title text-2xl">{{ category.name }}</h1>
        <p class="mt-2 opacity-80">
          {{ category.description || 'No description.' }}
        </p>
      </div>

      <!-- Divider -->
      <div class="divider md:divider-horizontal" />

      <!-- Right: subcategories -->
      <div class="md:flex-1">
        <h2 class="font-semibold mb-3">Subcategories</h2>

        <div v-if="subcategories.length" class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <RouterLink
            v-for="child in subcategories"
            :key="child.id"
            :to="`/categories/${child.id}`"
            class="btn btn-outline w-full justify-start"
          >
            {{ child.name }}
          </RouterLink>
        </div>

        <div v-else class="text-sm opacity-70">No subcategories.</div>
      </div>
    </div>
  </div>

  <div v-else class="card bg-base-100 shadow">
    <div class="card-body">
      <span class="loading loading-spinner loading-md"></span>
      <span class="ml-2">Loading…</span>
    </div>
  </div>
</template>
