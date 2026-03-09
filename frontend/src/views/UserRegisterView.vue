<script setup lang="ts">
import { ref } from 'vue'
import UserRegisterForm from '@/components/UserRegister.vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const store = useUserStore()
const router = useRouter()

const errorMessage = ref<string | null>(null)

async function handleCreate(payload: any) {
  errorMessage.value = null

  try {
    await store.create(payload)
    router.push({ path: '/account/login', query: { registered: 'true' } })
  } catch (error: any) {
    if (error?.response?.status === 400) {
      errorMessage.value = 'Det gick inte att skapa kontot. E-postadressen kanske redan används.'
    } else {
      errorMessage.value = 'Ett oväntat fel inträffade. Försök igen.'
    }
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <UserRegisterForm
      :submitting="store.loading"
      :serverFieldErrors="store.fieldErrors"
      :generalError="errorMessage"
      @create="handleCreate"
      @clear-error="errorMessage = null"
      @cancel="$router.push('/')"
    />
  </div>
</template>
