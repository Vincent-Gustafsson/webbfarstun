<script setup lang="ts">
import UserRegisterForm from '@/components/UserRegister.vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const store = useUserStore()
const router = useRouter()

async function handleCreate(payload: any) {
  const success = await store.create(payload)
  if (success) {
    router.push({ path: '/account/login', query: { registered: 'true' } })
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <UserRegisterForm
      :submitting="store.loading"
      :serverFieldErrors="store.fieldErrors"
      @create="handleCreate"
      @cancel="$router.push('/')"
    />
  </div>
</template>
