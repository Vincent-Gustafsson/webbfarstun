<script setup lang="ts">
import UserLogin from '@/components/UserLogin.vue'
import { userStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import type { UserRegister } from '@/types/user'
import { computed, watch } from 'vue'

const store = userStore()
const router = useRouter()

const isLoggedIn = computed(() => store.isLoggedIn)

watch(isLoggedIn, (now) => {
  if (now) router.replace('/')
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <UserLogin
      :submitting="store.submitting"
      :generalError="store.generalError"
      :serverFieldErrors="store.fieldErrors"
      @login="store.login"
      @clear-error="store.clearErrors"
      @cancel="$router.push('/')"
    />
  </div>
</template>
