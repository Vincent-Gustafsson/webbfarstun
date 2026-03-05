<script setup lang="ts">
import { reactive, ref, watch, onMounted, nextTick } from 'vue'

import { useProductGroupStore } from '@/stores/admin/productGroup'
import { useCategoryStore } from '@/stores/admin/category'
import ProductGroupVariationsPicker from '@/components/admin/productGroup/Create.vue'
import type { ProductGroupUpdate } from '@/types/admin/productGroup.ts'
const props = defineProps<{
  id: number
  submitting?: boolean
  generalError?: string | null
  serverFieldErrors?: Partial<Record<string, string>>
}>()

const emit = defineEmits<{
  (e: 'update', payload: ProductGroupUpdate): void
  (e: 'cancel'): void
  (e: 'clear-error'): void
}>()

const productGroupStore = useProductGroupStore()
const categoryStore = useCategoryStore()

const defaults = () => ({
  name: '',
  category_id: 0,
})

const form = reactive(defaults())
const submitted = ref(false)

const clientFieldErrors = ref<Partial<Record<'name' | 'category_id' | 'variation_ids', string>>>({})

const pickerRef = ref<InstanceType<typeof ProductGroupVariationsPicker> | null>(null)

function validateBasics() {
  const e: typeof clientFieldErrors.value = {}

  if (form.name.trim().length < 3) e.name = 'Name must be at least 3 characters'
  if (!form.category_id || form.category_id <= 0) e.category_id = 'Please select a category'

  clientFieldErrors.value = e
  return Object.keys(e).length === 0
}

function onSubmit() {
  emit('clear-error')

  const okBasics = validateBasics()
  const okPicker = pickerRef.value?.validate?.() ?? true
  if (!okBasics || !okPicker) {
    submitted.value = false
    return
  }

  submitted.value = true

  const variation_ids = pickerRef.value?.getVariationIds?.() ?? []

  const payload: ProductGroupUpdate = {
    name: form.name.trim(),
    category_id: form.category_id,
    variation_ids,
  }

  emit('update', payload)
}

watch(
  () => props.submitting,
  (now, prev) => {
    if (prev && !now && submitted.value) {
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
  () => form.category_id,
  (catId) => {
    if (clientFieldErrors.value.category_id && catId > 0) {
      clientFieldErrors.value = { ...clientFieldErrors.value, category_id: undefined }
    }
  },
)

onMounted(async () => {
  await categoryStore.fetchAll()

  const productGroup = await productGroupStore.fetchOne(props.id)

  if (productGroup) {
    form.name = productGroup.name
    form.category_id = productGroup.category_id
    await nextTick()
    if (productGroup.variation_ids && productGroup.variation_ids.length > 0) {
      pickerRef.value?.setVariationIds(productGroup.variation_ids)
    }
  }
})
</script>

<template>
  <form @submit.prevent="onSubmit" class="card bg-base-100 shadow-xl max-w-3xl">
    <div class="card-body space-y-6">
      <header class="space-y-1">
        <h2 class="card-title text-2xl">Update Product Group</h2>
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
            <input
              v-model="form.name"
              type="text"
              placeholder="e.g. iPhone 16 Series"
              :disabled="submitting"
              @input="emit('clear-error')"
            />
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
            v-model.number="form.category_id"
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

      <!-- Variations-->
      <div class="divider my-0">Variations</div>

      <ProductGroupVariationsPicker
        ref="pickerRef"
        :category-id="form.category_id"
        :disabled="!!submitting"
        embedded
      />

      <div v-if="serverFieldErrors?.variation_ids" class="alert alert-error">
        <span>{{ serverFieldErrors.variation_ids }}</span>
      </div>

      <footer class="card-actions justify-end gap-2">
        <button type="button" class="btn btn-ghost" @click="emit('cancel')">Cancel</button>

        <button type="submit" class="btn btn-primary" :disabled="submitting">
          <span v-if="submitting" class="loading loading-spinner loading-sm"></span>
          {{ submitting ? 'Saving…' : 'Update' }}
        </button>
      </footer>
    </div>
  </form>
</template>
