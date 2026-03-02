<script setup lang="ts">
import UserRegisterForm from '@/components/UserRegister.vue'
import { useUserStore } from '@/stores/user'

const store = useUserStore()
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <UserRegisterForm
      :submitting="store.loading"
      :serverFieldErrors="store.fieldErrors"
      @create="store.create"
      @cancel="$router.push('/')"
    />
  </div>
</template>
