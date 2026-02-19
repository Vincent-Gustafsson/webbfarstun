<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useCategoryStore } from '@/stores/category'
import NavBar from '@/components/NavBar.vue'
import CategoryTree from '@/components/CategoryTree.vue'
import CategoryPills from '@/components/CategoryPills.vue'

const categoryStore = useCategoryStore()

onMounted(() => {
  categoryStore.fetchAll()
})
</script>

<template>
  <div class="min-h-screen bg-base-200">
    <NavBar />

    <!-- Centered page container with bigger side margins -->
    <div class="px-6 py-4">
      <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
        <aside class="md:col-span-2">
          <div class="card bg-base-100 shadow">
            <div class="card-body">
              <h2 class="card-title text-base">Categories</h2>
              <CategoryTree />
            </div>
          </div>
        </aside>

        <main class="md:col-span-10">
          <CategoryPills />
          <RouterView />
        </main>
      </div>
    </div>
  </div>
</template>
