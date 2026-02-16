<script setup lang="ts">
import { reactive, watch, computed, onMounted, ref } from 'vue'
import type { ProductGroupCreate } from '@/types/admin/adminCreateProductGroup'
import { useCategoryStore } from '@/stores/admin/adminCategory'

const props = defineProps<{
  submitting?: boolean
  generalError?: string | null
  serverFieldErrors?: Partial<Record<keyof ProductGroupCreate, string>>
  categoryId: number
}>()

const emit = defineEmits<{
  (e: 'clear-error'): void
  (e: 'update:categoryId', value: number): void
}>()

const defaults = () => ({
  name: '',
  categoryId: 0,
})

const form = reactive(defaults())
const submitted = ref(false)

const clientFieldErrors = ref<Partial<Record<keyof ProductGroupCreate, string>>>({})
const hasServerFieldErrors = computed(
  () => !!props.serverFieldErrors && Object.keys(props.serverFieldErrors).length > 0,
)

const categoryStore = useCategoryStore()

const categoryModel = computed<number>({
  get: () => props.categoryId,
  set: (v) => emit('update:categoryId', v),
})

function validate() {
  const e: typeof clientFieldErrors.value = {}
  if (form.name.trim().length < 3) e.name = 'Name must be at least 3 characters'
  if (!categoryModel.value || categoryModel.value <= 0) e.category_id = 'Please select a category'
  clientFieldErrors.value = e
  return Object.keys(e).length === 0
}

function getPayload() {
  return {
    name: form.name,
    description: form.description,
    category_id: categoryModel.value,
  } as Pick<ProductGroupCreate, 'name' | 'description' | 'category_id'>
}

function resetForm() {
  Object.assign(form, defaults())
  categoryModel.value = 0
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

watch(
  () => categoryModel.value,
  (catId) => {
    if (clientFieldErrors.value.category_id && catId > 0) {
      clientFieldErrors.value = { ...clientFieldErrors.value, category_id: undefined }
    }
  },
)

onMounted(() => {
  categoryStore.fetchAll?.()
})

defineExpose({
  validate,
  getPayload,
  resetForm,
})
</script>

<template>
  <div class="card bg-base-100 shadow-xl max-w-3xl">
    <div class="card-body space-y-6">
      <header class="space-y-1">
        <h2 class="card-title text-2xl">Create Product Group</h2>
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
            <input v-model="form.name" type="text" placeholder="e.g. iPhone 16 Series" />
          </label>
          <label v-if="clientFieldErrors.name || serverFieldErrors?.name" class="label">
            <span class="label-text-alt text-error">
              {{ clientFieldErrors.name || serverFieldErrors?.name }}
            </span>
          </label>
        </div>

        <!-- Category -->
        <div class="form-control">
          <label class="label"><span class="label-text">Category</span></label>

          <select
            v-model.number="categoryModel"
            class="select select-bordered w-full"
            :class="
              clientFieldErrors.category_id || serverFieldErrors?.category_id ? 'select-error' : ''
            "
            :disabled="submitting || categoryStore.loading"
            @change="emit('clear-error')"
          >
            <option disabled :value="0">Select a category…</option>
            <option v-for="c in categoryStore.categories" :key="c.id" :value="c.id">
              {{ c.name }}
            </option>
          </select>

          <label
            v-if="clientFieldErrors.category_id || serverFieldErrors?.category_id"
            class="label"
          >
            <span class="label-text-alt text-error">
              {{ clientFieldErrors.category_id || serverFieldErrors?.category_id }}
            </span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>
