<script setup lang="ts">
import UserLogin from '@/components/UserLogin.vue'
import { userStore } from '@/stores/user'
import { useRouter } from 'vue-router'
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
      :serverFieldErrors="store.fieldErrors"
      @login="store.login"
      @cancel="$router.push('/')"
    />
  </div>
</template>
