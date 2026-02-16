<script setup lang="ts">
import { reactive, watch, computed, onMounted, ref } from 'vue'
import type { ProductGroupCreate } from '@/types/admin/adminCreateProductGroup'
import { useProductGroupStore } from '@/stores/admin/adminCreateProductGroup'

import { useCategoryStore } from '@/stores/admin/adminCategory'
import { useVariationStore } from '@/stores/admin/adminVariation'

const props = defineProps<{
  submitting?: boolean
  generalError?: string | null
  serverFieldErrors?: Partial<Record<keyof ProductGroupCreate, string>>
  createdCategoryId?: number | null
}>()

const emit = defineEmits<{
  (e: 'create', payload: ProductGroupCreate): void
  (e: 'cancel'): void
  (e: 'clear-error'): void
}>()

const defaults = (): ProductGroupCreate => ({
  name: '',
  description: '',
  category_id: 0 as any,
})

const form = reactive<ProductGroupCreate>(defaults())
const submitted = ref(false)

const clientFieldErrors = ref<Partial<Record<keyof ProductGroupCreate, string>>>({})
const hasServerFieldErrors = computed(
  () => !!props.serverFieldErrors && Object.keys(props.serverFieldErrors).length > 0,
)

function validate() {
  const e: typeof clientFieldErrors.value = {}
  if (form.name.trim().length < 3) e.name = 'Name must be at least 3 characters'
  if (!(form as any).category_id || (form as any).category_id <= 0)
    e.category_id = 'Please select a category'
  clientFieldErrors.value = e
  return Object.keys(e).length === 0
}

function resetForm() {
  Object.assign(form, defaults())
  variationRows.value = []
  variationRowErrors.value = {}
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

// stores
const productGroupStore = useProductGroupStore()
const categoryStore = useCategoryStore()
const variationStore = useVariationStore()

onMounted(() => {
  categoryStore.fetchAll?.()
  variationStore.fetchAll?.()
  productGroupStore.fetchAll?.()
})

/* -----------------------------
   Variations (+ add row) logic
------------------------------ */

type VariationRow = { variation_id: number }

const makeVariationRow = (): VariationRow => ({ variation_id: 0 })

const variationRows = ref<VariationRow[]>([])
const variationRowErrors = ref<Record<number, string>>({})

const filteredVariations = computed(() => {
  const catId = (form as any).category_id as number
  if (!catId) return []
  return (variationStore.variations ?? []).filter((v: any) => v.category_id === catId)
})

function addVariationRow() {
  variationRows.value.push(makeVariationRow())
}

function removeVariationRow(i: number) {
  variationRows.value.splice(i, 1)
  // keep errors in sync
  validateVariationRows()
}

function validateVariationRows() {
  const rows = variationRows.value

  // variations are OPTIONAL -> no rows means valid
  if (rows.length === 0) {
    variationRowErrors.value = {}
    return true
  }

  const errs: Record<number, string> = {}

  // count duplicates (ignore 0)
  const counts = new Map<number, number>()
  rows.forEach((r) => {
    if (r.variation_id > 0) counts.set(r.variation_id, (counts.get(r.variation_id) ?? 0) + 1)
  })

  rows.forEach((r, i) => {
    if (r.variation_id <= 0) {
      errs[i] = 'Please select a variation'
    } else if ((counts.get(r.variation_id) ?? 0) > 1) {
      errs[i] = 'This variation is already selected'
    }
  })

  variationRowErrors.value = errs
  return Object.keys(errs).length === 0
}

// when category changes -> clear rows (because subset changed)
watch(
  () => (form as any).category_id,
  (catId) => {
    variationRows.value = []
    variationRowErrors.value = {}

    if (clientFieldErrors.value.category_id && catId > 0) {
      clientFieldErrors.value = { ...clientFieldErrors.value, category_id: undefined }
    }
  },
)

// live revalidate if user changes selections and there are errors showing
watch(
  () => variationRows.value.map((r) => r.variation_id),
  () => {
    if (Object.keys(variationRowErrors.value).length) validateVariationRows()
  },
  { deep: true },
)

function onSubmit() {
  emit('clear-error')

  const okFields = validate()
  const okVariations = validateVariationRows()

  if (!okFields || !okVariations) {
    submitted.value = false
    return
  }

  submitted.value = true

  const variation_ids = variationRows.value.map((r) => r.variation_id).filter((id) => id > 0)

  const payload = {
    ...form,
    category_id: (form as any).category_id,
    variation_ids,
  }

  emit('create', payload as any)
}
</script>

<template>
  <form @submit.prevent="onSubmit" class="card bg-base-100 shadow-xl max-w-3xl">
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
            v-model.number="(form as any).category_id"
            class="select select-bordered w-full"
            :class="
              clientFieldErrors.category_id || serverFieldErrors?.category_id ? 'select-error' : ''
            "
            :disabled="submitting || categoryStore.loading"
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

        <!-- Variations (+) -->
        <div class="md:col-span-2 space-y-2">
          <div class="flex items-center justify-between">
            <label class="label p-0">
              <span class="label-text">Variations for this product group</span>
            </label>

            <button
              type="button"
              class="btn btn-outline btn-sm btn-square"
              @click="addVariationRow"
              :disabled="submitting || !(form as any).category_id"
              title="Add variation"
            >
              +
            </button>
          </div>

          <div v-if="!(form as any).category_id" class="text-sm opacity-70">
            Select a category first to choose variations.
          </div>

          <div v-else-if="filteredVariations.length === 0" class="text-sm opacity-70">
            This category has no variations.
          </div>

          <div v-else-if="variationRows.length === 0" class="text-sm opacity-70">
            No variations added (optional). Click + to add.
          </div>

          <div class="space-y-2">
            <div
              v-for="(row, i) in variationRows"
              :key="i"
              class="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-2 items-end"
            >
              <div class="form-control">
                <label class="label"><span class="label-text">Variation</span></label>
                <select
                  v-model.number="row.variation_id"
                  class="select select-bordered w-full"
                  :class="variationRowErrors[i] ? 'select-error' : ''"
                  :disabled="submitting"
                >
                  <option disabled :value="0">Select variation…</option>
                  <option v-for="v in filteredVariations" :key="v.id" :value="v.id">
                    {{ v.name }}
                  </option>
                </select>

                <label v-if="variationRowErrors[i]" class="label">
                  <span class="label-text-alt text-error">{{ variationRowErrors[i] }}</span>
                </label>
              </div>

              <button
                type="button"
                class="btn btn-ghost btn-square"
                @click="removeVariationRow(i)"
                title="Remove"
              >
                ✕
              </button>
            </div>
          </div>
        </div>

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
          {{ submitting ? 'Saving…' : 'Create product group' }}
        </button>
      </footer>
    </div>
  </form>
</template>
