<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import ThemeToggle from '@/components/ThemeToggle.vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const accountStore = useUserStore()

const isLoggedIn = computed(() => accountStore.isLoggedIn)

async function logout() {
  await accountStore.logout()
  router.push('/')
}

onMounted(() => {
  accountStore.fetchMe?.()
})
</script>

<template>
  <!-- Top banner -->
  <div class="w-full bg-neutral text-neutral-content text-xs">
    <div class="mx-auto max-w-7xl px-4 py-2 flex items-center gap-4 overflow-x-auto">
      <span class="whitespace-nowrap"> <span class="text-success">✓</span> Free shipping </span>
      <span class="whitespace-nowrap">
        <span class="text-success">✓</span> 30 day money-back guarantee
      </span>
      <span class="whitespace-nowrap"> <span class="text-success">✓</span> Free returns </span>
      <span class="whitespace-nowrap">
        <span class="text-success">✓</span> Orders before 17:00 ships today
      </span>
    </div>
  </div>

  <!-- Navbar -->
  <div class="bg-base-100 shadow">
    <div class="navbar mx-auto max-w-7xl px-4 gap-3">
      <!-- Left -->
      <div class="flex-none">
        <RouterLink to="/" class="btn btn-ghost text-xl">Webbfarstun</RouterLink>
      </div>

      <!-- Middle (THIS must be flex-1, not navbar-center) -->
      <div class="flex-1 min-w-0">
        <label class="input input-bordered flex items-center gap-2 w-full">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            class="h-4 w-4 opacity-70"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-4.35-4.35m1.35-5.65a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>

          <input class="grow min-w-0" type="text" placeholder="Search products…" />
        </label>
      </div>

      <!-- Right -->
      <div class="flex-none flex items-center gap-2">
        <RouterLink v-if="!isLoggedIn" to="/account/login" class="btn btn-ghost whitespace-nowrap">
          Login
        </RouterLink>
        <button v-else class="btn btn-ghost whitespace-nowrap" type="button" @click="logout">
          Logout
        </button>
        <RouterLink to="/cart" class="btn btn-primary whitespace-nowrap">Cart</RouterLink>
        <ThemeToggle />
      </div>
    </div>
  </div>
</template>
