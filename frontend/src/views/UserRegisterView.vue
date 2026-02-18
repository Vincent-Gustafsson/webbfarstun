<script setup lang="ts">
import UserRegisterForm from '@/components/UserRegister.vue'
import { userStore } from '@/stores/user'
import type { UserRegister } from '@/types/user'

const store = userStore()
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <UserRegisterForm
      :submitting="store.loading"
      :generalError="store.generalError"
      :serverFieldErrors="store.fieldErrors"
      @create="store.create"
      @clear-error="store.clearErrors"
      @cancel="$router.push('/')"
    />
  </div>
</template>
