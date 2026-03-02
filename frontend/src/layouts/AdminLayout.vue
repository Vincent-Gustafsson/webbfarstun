<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, RouterLink, RouterView } from 'vue-router'

const route = useRoute()

const title = computed(() => {
  return (route.meta?.title as string) ?? 'Shop Panel'
})

const nav = [{ to: '/admin', label: 'Dashboard' }]

const createLinks = [
  { to: '/admin/products', label: 'Products' },
  { to: '/admin/categories', label: 'Categories' },
  { to: '/admin/product-groups', label: 'Product groups' },
]

const UpdateLinks = [
  { to: '/admin/list/categories', label: 'Categories' },
  { to: '/admin/list/products', label: 'Products' },
  { to: '/admin/list/product-groups', label: 'Product groups' },
]
</script>

<template>
  <div class="drawer lg:drawer-open min-h-screen bg-base-100">
    <input id="admin-drawer" type="checkbox" class="drawer-toggle" />

    <!-- Main -->
    <div class="drawer-content flex flex-col">
      <!-- Top bar -->
      <nav class="navbar w-full bg-base-300 border-b border-base-content/10">
        <div class="flex-none lg:hidden">
          <label for="admin-drawer" aria-label="open sidebar" class="btn btn-square btn-ghost">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="size-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M4 6h16" />
              <path d="M4 12h16" />
              <path d="M4 18h16" />
            </svg>
          </label>
        </div>

        <div class="flex-1 px-4">
          <div class="font-semibold text-lg leading-none">{{ title }}</div>
          <div class="text-xs opacity-60">Shop panel</div>
        </div>
      </nav>

      <!-- Page -->
      <div class="p-4 md:p-6">
        <RouterView />
      </div>
    </div>

    <!-- Sidebar -->
    <div class="drawer-side">
      <label for="admin-drawer" aria-label="close sidebar" class="drawer-overlay"></label>

      <aside class="w-64 bg-base-200 min-h-full border-r border-base-content/10">
        <div class="px-4 py-4 text-center">
          <div class="font-bold text-lg">Manage</div>
          <div class="text-xs opacity-60">Navigation</div>
        </div>

        <div class="px-3 pb-6 flex justify-center">
          <ul class="menu menu-md gap-2 w-full max-w-[14rem]">
            <!-- Dashboard -->
            <li v-for="l in nav" :key="l.to">
              <RouterLink
                :to="l.to"
                class="rounded-lg px-3 py-2 justify-center text-center hover:bg-base-300 transition"
                :class="{
                  'bg-primary text-primary-content hover:bg-primary/90': $route.path === l.to,
                }"
              >
                <span class="font-medium">{{ l.label }}</span>
              </RouterLink>
            </li>

            <!-- Create dropdown -->
            <li>
              <details open class="w-full">
                <summary class="justify-center text-center font-semibold">Create</summary>

                <ul class="mt-2 gap-2">
                  <li v-for="l in createLinks" :key="l.to">
                    <RouterLink
                      :to="l.to"
                      class="rounded-lg px-3 py-2 justify-center text-center hover:bg-base-300 transition"
                      :class="{
                        'bg-primary text-primary-content hover:bg-primary/90':
                          $route.path.startsWith(l.to),
                      }"
                    >
                      <span class="font-medium"> {{ l.label }}</span>
                    </RouterLink>
                  </li>
                </ul>
              </details>
            </li>
            <!-- Update dropdown -->
            <li>
              <details open class="w-full">
                <summary class="justify-center text-center font-semibold">List</summary>

                <ul class="mt-2 gap-2">
                  <li v-for="l in UpdateLinks" :key="l.to">
                    <RouterLink
                      :to="l.to"
                      class="rounded-lg px-3 py-2 justify-center text-center hover:bg-base-300 transition"
                      :class="{
                        'bg-primary text-primary-content hover:bg-primary/90':
                          $route.path.startsWith(l.to),
                      }"
                    >
                      <span class="font-medium"> {{ l.label }}</span>
                    </RouterLink>
                  </li>
                </ul>
              </details>
            </li>
          </ul>
        </div>
      </aside>
    </div>
  </div>
</template>
