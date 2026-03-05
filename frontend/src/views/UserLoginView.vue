<script setup lang="ts">
import UserLogin from '@/components/UserLogin.vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
const store = useUserStore()
const router = useRouter()
const route = useRoute()

const isLoggedIn = computed(() => store.isLoggedIn)
const showSuccessMessage = computed(() => route.query.registered === 'true')

watch(isLoggedIn, (now) => {
  if (now) router.replace('/')
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="w-full max-w-sm">
      <div v-if="showSuccessMessage" class="alert alert-success shadow-lg mb-6">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="stroke-current shrink-0 h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <span>Account created! Please sign in.</span>
      </div>
      <UserLogin
        :serverFieldErrors="store.fieldErrors"
        @login="store.login"
        @cancel="$router.push('/')"
      />
    </div>
  </div>
</template>
