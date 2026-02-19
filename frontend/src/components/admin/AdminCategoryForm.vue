<script setup lang="ts">
import { reactive, watch, computed, onMounted, ref } from 'vue'
import type { Category, CategoryCreate, CategoryUpdate } from '@/types/admin/adminCategory'
import { useCategoryStore } from '@/stores/admin/adminCategory'
import { watchEffect } from 'vue'

const props = defineProps<{
  mode?: 'create' | 'update'
  category?: Category | null
  submitting?: boolean
  generalError?: string | null
  serverFieldErrors?: Partial<Record<keyof CategoryCreate, string>>
  createdCategoryId?: number | null
}>()

const emit = defineEmits<{
  (e: 'create', payload: CategoryCreate): void
  (e: 'update', payload: CategoryUpdate): void
  (e: 'cancel'): void
  (e: 'clear-error'): void
}>()

const defaults = (): CategoryCreate => ({
  name: '',
  description: '',
  category_parent_id: null as any,
  is_container: false,
})

const form = reactive<CategoryCreate>(defaults())
const submitted = ref(false)

const clientFieldErrors = ref<Partial<Record<keyof CategoryCreate, string>>>({})
const hasServerFieldErrors = computed(
  () => !!props.serverFieldErrors && Object.keys(props.serverFieldErrors).length > 0,
)

function validate() {
  const e: typeof clientFieldErrors.value = {}
  if (form.name.trim().length < 3) e.name = 'Name must be at least 3 characters'
  clientFieldErrors.value = e
  return Object.keys(e).length === 0
}

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

watch(
  () => form.name,
  (name) => {
    if (clientFieldErrors.value.name && name.trim().length >= 3) {
      clientFieldErrors.value = { ...clientFieldErrors.value, name: undefined }
    }
  },
)

function onSubmit() {
  emit('clear-error')
  if (!validate()) return

  if (props.mode === 'update') {
    const payload: CategoryUpdate = {
      name: form.name,
      description: form.description,
      is_container: form.is_container,
      category_parent_id: form.category_parent_id,
    }
    emit('update', payload)
  } else {
    const payload: CategoryCreate = {
      name: form.name,
      description: form.description,
      is_container: form.is_container,
      ...(form.category_parent_id != null ? { category_parent_id: form.category_parent_id } : {}),
    } as any
    emit('create', payload)
  }
}

const categoryStore = useCategoryStore()
onMounted(() => {
  categoryStore.fetchAll?.()
})

//Update form mode

watchEffect(() => {
  if (props.mode === 'update' && props.category) {
    form.name = props.category.name ?? ''
    form.description = props.category.description ?? ''
    form.category_parent_id = props.category.category_parent_id ?? (null as any)
    form.is_container = !!props.category.is_container
  }
})
</script>

<template>
  <form @submit.prevent="onSubmit" class="card bg-base-100 shadow-xl max-w-3xl">
    <div class="card-body space-y-6">
      <header class="space-y-1">
        <h2 class="card-title text-2xl">
          {{ props.mode === 'update' ? 'Update Category' : 'Create Category' }}
        </h2>

        <p v-if="createdCategoryId" class="text-sm opacity-70">
          Category created. You can now add variations and options below.
        </p>
      </header>

      <div v-if="generalError" class="alert alert-error">
        <span>{{ generalError }}</span>
      </div>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <!-- Name -->
        <div class="form-control">
          <label class="label"><span class="label-text">Name</span></label>
          <label
            class="input input-bordered flex items-center gap-2"
            :class="clientFieldErrors.name || serverFieldErrors?.name ? 'input-error' : ''"
          >
            <input v-model="form.name" type="text" placeholder="e.g. iPhone" />
          </label>
          <label v-if="clientFieldErrors.name || serverFieldErrors?.name" class="label">
            <span class="label-text-alt text-error">
              {{ clientFieldErrors.name || serverFieldErrors?.name }}
            </span>
          </label>
        </div>

        <!-- Parent Category -->
        <div class="form-control">
          <label class="label"><span class="label-text">Parent Category</span></label>

          <select
            v-model="form.category_parent_id"
            class="select select-bordered w-full"
            :class="
              clientFieldErrors.category_parent_id || serverFieldErrors?.category_parent_id
                ? 'select-error'
                : ''
            "
            :disabled="submitting || categoryStore.loading"
          >
            <option :value="null">None</option>
            <option v-for="c in categoryStore.categories" :key="c.id" :value="c.id">
              {{ c.name }}
            </option>
          </select>

          <label
            v-if="clientFieldErrors.category_parent_id || serverFieldErrors?.category_parent_id"
            class="label"
          >
            <span class="label-text-alt text-error">
              {{ clientFieldErrors.category_parent_id || serverFieldErrors?.category_parent_id }}
            </span>
          </label>
        </div>

        <!-- Container -->
        <fieldset class="fieldset bg-base-100 border-base-300 rounded-box w-full border p-4">
          <legend class="fieldset-legend">Container</legend>
          <label class="label cursor-pointer gap-3 justify-start">
            <input
              v-model="form.is_container"
              type="checkbox"
              class="checkbox"
              :disabled="submitting"
            />
            <span>Is container</span>
          </label>
        </fieldset>

        <!-- Description -->
        <div class="form-control md:col-span-2">
          <label class="label"><span class="label-text">Description</span></label>
          <textarea
            v-model="form.description"
            rows="4"
            placeholder="Short description…"
            class="textarea textarea-bordered w-full"
          />
        </div>
      </div>

      <footer class="card-actions justify-end gap-2">
        <button type="button" class="btn btn-ghost" @click="emit('cancel')">Cancel</button>
        <button type="submit" class="btn btn-primary" :disabled="submitting">
          <span v-if="submitting" class="loading loading-spinner loading-sm"></span>
          {{ submitting ? 'Saving…' : 'Submit' }}
        </button>
      </footer>
    </div>
  </form>
</template>
