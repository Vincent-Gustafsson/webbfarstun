<script setup lang="ts">
import UserRegisterForm from '@/components/UserRegister.vue'
import { userStore } from '@/stores/user'
import type { UserRegister } from '@/types/user'

const store = userStore()

async function register(payload: UserRegister) {
  await store.register(payload)
}
</script>

<template>
  <UserRegisterForm
    :submitting="store.submitting"
    :generalError="store.generalError"
    :serverFieldErrors="store.fieldErrors"
    @create="register"
    @clear-error="store.clearErrors"
    @cancel="$router.push('/')"
  />
</template>
