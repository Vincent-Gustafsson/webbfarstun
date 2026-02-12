<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import CategoryTree from '@/components/CategoryTree.vue'
import { useCategoryStore } from '@/stores/category'

const categoryStore = useCategoryStore()

onMounted(() => {
  categoryStore.fetchAll()
})
</script>

<template>
  <div class="min-h-screen bg-base-200">
    <Navbar />

    <!-- Centered page container with bigger side margins -->
    <div class="mx-auto max-w-7xl px-6 py-4">
      <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
        <aside class="md:col-span-3">
          <div class="card bg-base-100 shadow">
            <div class="card-body">
              <h2 class="card-title text-base">Categories</h2>
              <CategoryTree />
            </div>
          </div>
        </aside>

        <main class="md:col-span-9">
          <RouterView />
        </main>
      </div>
    </div>
  </div>
</template>
