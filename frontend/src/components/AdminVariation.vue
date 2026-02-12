<script setup lang="ts">
import { reactive, watch, computed, onMounted, ref } from 'vue'
import type { VariationCreate } from '@/types/adminVariation'
import { useCategoryStore } from '@/stores/category'

const props = defineProps<{
  submitting?: boolean
  error?: string | null
}>()

const emit = defineEmits<{
  (e: 'create', payload: VariationCreate): void
  (e: 'cancel'): void
  (e: 'clear-error'): void
}>()

const defaults = (): VariationCreate => ({
  name: '',
  category_id: 0,
})

const form = reactive<VariationCreate>(defaults())
const submitted = ref(false)

function resetForm() {
  Object.assign(form, defaults())
  category_id.value = null
}

const categoryError = ref<string | null>(null)
const generalError = computed(() => props.error)

watch(
  () => form.category_id,
  () => {
    categoryError.value = null
    emit('clear-error')
  },
)

watch(
  () => props.submitting,
  (now, prev) => {
    if (prev && !now && submitted.value) {
      if (!props.error) resetForm()
      submitted.value = false
    }
  },
)

function onSubmit() {
  submitted.value = true
  categoryError.value = null
  emit('clear-error')
  emit('create', { ...form })
}

const categoryStore = useCategoryStore()

onMounted(() => {
  if (categoryStore.categories?.length) return
  categoryStore.fetchAll?.()
})
</script>

<template>
  <form @submit.prevent="onSubmit" class="card bg-base-100 shadow-xl max-w-2xl">
    <div class="card-body space-y-6">
      <header class="space-y-1">
        <h2 class="card-title text-2xl">Create variation</h2>
        <p class="text-sm opacity-70">Fill in the details below and save.</p>
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
          <input
            v-model="form.name"
            type="text"
            placeholder="e.g. Winter Jacket"
            class="input input-bordered w-full"
          />
        </div>

        <!-- Category group -->
        <div class="form-control">
          <label class="label">
            <span class="label-text">Category group</span>
          </label>

          <select
            v-model.number="form.category_id"
            class="select select-bordered w-full"
            :disabled="submitting || categoryStore.loading"
          >
            <option disabled :value="0">Select a category group…</option>

            <option v-for="g in categoryStore.categories" :key="g.id" :value="g.id">
              {{ g.name }}
            </option>
          </select>
          <label v-if="categoryError" class="label">
            <span class="label-text-alt text-error">{{ categoryError }}</span>
          </label>

          <label v-if="categoryStore.error" class="label">
            <span class="label-text-alt text-error">{{ categoryStore.error }}</span>
          </label>
        </div>

        <div class="hidden md:block"></div>
      </div>
      <footer class="card-actions justify-end gap-2">
        <button type="button" class="btn btn-ghost" @click="emit('cancel')">Cancel</button>

        <button type="submit" class="btn btn-primary" :disabled="submitting">
          <span v-if="submitting" class="loading loading-spinner loading-sm"></span>
          {{ submitting ? 'Saving…' : 'Create variation' }}
        </button>
      </footer>
    </div>
  </form>
</template>
