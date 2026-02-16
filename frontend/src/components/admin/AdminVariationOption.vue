<script setup lang="ts">
import { reactive, watch, computed, onMounted, ref } from 'vue'
import type { VariationOptionCreate } from '@/types/admin/adminVariationOption'
import { useVariationStore } from '@/stores/admin/adminVariation'

const props = defineProps<{
  submitting?: boolean
  generalError?: string | null
  serverFieldErrors?: Partial<Record<keyof VariationOptionCreate, string>>
}>()

type VariationOptionsCreateMany = {
  variation_id: number
  values: string[]
}

const emit = defineEmits<{
  (e: 'create-many', payload: VariationOptionsCreateMany): void
  (e: 'cancel'): void
  (e: 'clear-error'): void
}>()

const defaults = (): VariationOptionCreate => ({
  value: '',
  variation_id: 0,
})

const clientFieldErrors = ref<Partial<Record<keyof VariationOptionCreate, string>>>({})
const hasServerFieldErrors = computed(
  () => !!props.serverFieldErrors && Object.keys(props.serverFieldErrors).length > 0,
)

function validate() {
  const e: typeof clientFieldErrors.value = {}
  if (form.value.trim().length < 3) e.value = 'Value must be at least 3 characters'
  if (form.variation_id <= 0) e.variation_id = 'Please select a Variation'

  clientFieldErrors.value = e
  return Object.keys(e).length === 0
}

//Clear form on succesfull submit
const form = reactive<VariationOptionCreate>(defaults())
const submitted = ref(false)

function resetForm() {
  Object.assign(form, defaults())
}

watch(
  () => props.submitting,
  (now, prev) => {
    if (prev && !now && submitted.value) {
      if (!props.generalError && !hasServerFieldErrors.value) resetForm()
      submitted.value = false
    }
  },
)

//reset error when valid
watch(
  () => form.value,
  (value) => {
    if (clientFieldErrors.value.value && value.trim().length >= 3) {
      clientFieldErrors.value = { ...clientFieldErrors.value, value: undefined }
    }
  },
)

watch(
  () => form.variation_id,
  (variation_id) => {
    if (clientFieldErrors.value.variation_id && variation_id > 0) {
      clientFieldErrors.value = { ...clientFieldErrors.value, variation_id: undefined }
    }
  },
)

//Cast error if it isnt category error
watch(
  () => props.error,
  (msg) => {
    if (!msg) {
      return
    }
  },
)

function onSubmit() {
  emit('clear-error')

  if (!validate()) {
    submitted.value = false
    return
  }

  submitted.value = true

  emit('create', { ...form })
}

//Dropdown of variations
const variationStore = useVariationStore()

onMounted(() => {
  if (variationStore.variations?.length) return
  variationStore.fetchAll?.()
})
</script>

<template>
  <form @submit.prevent="onSubmit" class="card bg-base-100 shadow-xl max-w-2xl">
    <div class="card-body space-y-6">
      <header class="space-y-1">
        <h2 class="card-title text-2xl">Create variation option</h2>
      </header>

      <div v-if="generalError" class="alert alert-error">
        <span>{{ generalError }}</span>
      </div>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <!-- Name -->
        <div class="form-control">
          <label class="label">
            <span class="label-text">Name</span>
          </label>
          <label
            class="input input-bordered flex items-center gap-2"
            :class="clientFieldErrors.value || serverFieldErrors?.value ? 'input-error' : ''"
          >
            <input v-model="form.value" type="text" placeholder="e.g. Winter Jacket" class="" />
          </label>
          <label v-if="clientFieldErrors.value || serverFieldErrors?.value" class="label">
            <span class="label-text-alt text-error">{{
              clientFieldErrors.value || serverFieldErrors?.value
            }}</span>
          </label>
        </div>

        <!-- Variation group -->
        <div class="form-control">
          <label class="label">
            <span class="label-text">Variation group</span>
          </label>

          <select
            v-model.number="form.variation_id"
            class="select select-bordered w-full"
            :class="
              clientFieldErrors.variation_id || serverFieldErrors?.variation_id
                ? 'select-error'
                : ''
            "
            :disabled="submitting || variationStore.loading"
          >
            <option disabled :value="0">Select a category group…</option>

            <option v-for="g in variationStore.variations" :key="g.id" :value="g.id">
              {{ g.name }}
            </option>
          </select>

          <label
            v-if="clientFieldErrors.variation_id || serverFieldErrors?.variation_id"
            class="label"
          >
            <span class="label-text-alt text-error">{{
              clientFieldErrors.variation_id || serverFieldErrors?.variation_id
            }}</span>
          </label>

          <label v-if="variationStore.error" class="label">
            <span class="label-text-alt text-error">{{ variationStore.error }}</span>
          </label>
        </div>

        <div class="hidden md:block"></div>
      </div>
      <footer class="card-actions justify-end gap-2">
        <button type="button" class="btn btn-ghost" @click="emit('cancel')">Cancel</button>

        <button type="submit" class="btn btn-primary" :disabled="submitting">
          <span v-if="submitting" class="loading loading-spinner loading-sm"></span>
          {{ submitting ? 'Saving…' : 'Create variation Option' }}
        </button>
      </footer>
    </div>
  </form>
</template>
