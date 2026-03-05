<script setup lang="ts">
import { reactive, ref, watch, computed } from 'vue'
import type { UserRegister } from '@/types/user'

const props = defineProps<{
  submitting?: boolean
  generalError?: string | null
  serverFieldErrors?: Partial<Record<keyof UserRegister, string>>
}>()

const emit = defineEmits<{
  (e: 'create', payload: UserRegister): void
  (e: 'cancel'): void
  (e: 'clear-error'): void
}>()

const defaults = (): UserRegister => ({
  name: '',
  email: '',
  password: '',
})

const form = reactive<UserRegister>(defaults())
const submitted = ref(false)

const clientFieldErrors = ref<Partial<Record<keyof UserRegister, string>>>({})
const hasServerFieldErrors = computed(
  () => !!props.serverFieldErrors && Object.keys(props.serverFieldErrors).length > 0,
)

function validate() {
  const e: typeof clientFieldErrors.value = {}
  if (form.name.trim().length < 3) e.name = 'Name must be at least 3 characters'
  if (!form.email.trim()) e.email = 'Email is required'
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) e.email = 'Email is not valid'

  if (form.email.trim().length < 3) e.email = 'Email must be at least 3 characters'
  if (form.password.trim().length < 3) e.password = 'Password must be at least 3 characters'

  clientFieldErrors.value = e
  return Object.keys(e).length === 0
}

function resetForm() {
  Object.assign(form, defaults())
}

watch(form, () => {
  clientFieldErrors.value = {}
})

function onSubmit() {
  emit('clear-error')

  if (!validate()) {
    submitted.value = false
    return
  }

  submitted.value = true

  const payload: UserRegister = {
    email: form.email,
    password: form.password,
    name: form.name,
  }

  emit('create', payload)
}

watch(
  () => props.submitting,
  (now, prev) => {
    if (prev && !now && submitted.value) {
      if (!props.generalError && !hasServerFieldErrors.value) resetForm()
    }
    submitted.value = false
  },
)
</script>

<template>
  <form novalidate @submit.prevent="onSubmit" class="card bg-base-100 shadow-xl max-w-sm w-full">
    <div class="card-body space-y-4">
      <header>
        <h2 class="card-title text-2xl">Create Account</h2>
      </header>

      <div v-if="generalError" class="alert alert-error">
        <span>{{ generalError }}</span>
      </div>

      <!-- Column layout -->
      <div class="flex flex-col gap-4">
        <!-- Name -->

        <div class="form-control">
          <label class="label">
            <span class="label-text">Name</span>
          </label>
          <label
            class="input validator"
            :class="clientFieldErrors.name || serverFieldErrors?.name ? 'input-error' : ''"
          >
            <svg class="h-[1em] opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <g
                stroke-linejoin="round"
                stroke-linecap="round"
                stroke-width="2.5"
                fill="none"
                stroke="currentColor"
              >
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </g>
            </svg>
            <input
              v-model="form.name"
              type="text"
              required
              placeholder="Your Name"
              pattern="[A-Za-z][A-Za-z0-9\-]*"
              minlength="3"
              maxlength="30"
              title="Only letters, numbers or dash"
            />
          </label>
          <p class="validator-hint">
            Must be 3 to 30 characters
            <br />containing only letters, numbers or dash
          </p>
          <label v-if="clientFieldErrors.name || serverFieldErrors?.name" class="label">
            <span class="label-text-alt text-error">
              {{ clientFieldErrors.name || serverFieldErrors?.name }}
            </span>
          </label>
        </div>
        <!-- Email -->
        <div class="form-control">
          <label class="label">
            <span class="label-text">Email</span>
          </label>
          <label
            class="input input-bordered flex items-center gap-2"
            :class="clientFieldErrors.email || serverFieldErrors?.email ? 'input-error' : ''"
          >
            <svg class="h-[1em] opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <g
                stroke-linejoin="round"
                stroke-linecap="round"
                stroke-width="2.5"
                fill="none"
                stroke="currentColor"
              >
                <rect width="20" height="16" x="2" y="4" rx="2"></rect>
                <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
              </g>
            </svg>
            <input v-model="form.email" type="email" placeholder="mail@example.com" class="grow" />
          </label>
          <label v-if="clientFieldErrors.email || serverFieldErrors?.email" class="label">
            <span class="label-text-alt text-error">
              {{ clientFieldErrors.email || serverFieldErrors?.email }}
            </span>
          </label>
        </div>

        <div class="form-control">
          <label class="label">
            <span class="label-text">Password</span>
          </label>
          <label class="input validator">
            <svg class="h-[1em] opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <g
                stroke-linejoin="round"
                stroke-linecap="round"
                stroke-width="2.5"
                fill="none"
                stroke="currentColor"
              >
                <path
                  d="M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z"
                ></path>
                <circle cx="16.5" cy="7.5" r=".5" fill="currentColor"></circle>
              </g>
            </svg>
            <input
              v-model="form.password"
              type="password"
              required
              placeholder="Password"
              minlength="8"
              pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"
              title="Must be more than 8 characters, including number, lowercase letter, uppercase letter"
            />
          </label>
          <p class="validator-hint hidden">
            Must be more than 8 characters, including
            <br />At least one number <br />At least one lowercase letter <br />At least one
            uppercase letter
          </p>
        </div>
        <RouterLink to="/account/login" class="link link-primary text-center">
          Already have an account? Sign in
        </RouterLink>

        <!-- Actions -->
        <div class="flex flex-col gap-2">
          <button type="submit" class="btn btn-primary w-full" :disabled="submitting">
            <span v-if="submitting" class="loading loading-spinner loading-sm"></span>
            {{ submitting ? 'Saving…' : 'Create Account' }}
          </button>
          <button type="button" class="btn btn-ghost w-full" @click="emit('cancel')">Cancel</button>
        </div>
      </div>
    </div>
  </form>
</template>
