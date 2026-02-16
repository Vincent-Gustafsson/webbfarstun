<script setup lang="ts">
import { reactive, watch, computed, onMounted, ref } from 'vue'
import type { ProductCreate } from '@/types/admin/adminCreateProduct'
import { useProductGroupStore } from '@/stores/admin/adminCreateProductGroup'
import { useVariationStore } from '@/stores/admin/adminVariation'

const props = defineProps<{
  submitting?: boolean
  generalError?: string | null
  serverFieldErrors?: Partial<Record<keyof ProductCreate, string>>
}>()

type ProductVariation = {
  variation_id: number
}

const makeVariationRow = (): ProductVariation => ({
  variation_id: 0,
})

const emit = defineEmits<{
  (e: 'create', payload: ProductCreate): void
  (e: 'cancel'): void
  (e: 'clear-error'): void
}>()

const defaults = (): ProductCreate => ({
  name: '',
  product_group_id: 0,
  price: 0,
  stock_qty: 0,
  description: '',
  sku: '',
  options: [] as any,
})

const clientFieldErrors = ref<Partial<Record<keyof ProductCreate, string>>>({})
const hasServerFieldErrors = computed(
  () => !!props.serverFieldErrors && Object.keys(props.serverFieldErrors).length > 0,
)

//validate values

function validate() {
  const e: typeof clientFieldErrors.value = {}

  if (form.name.trim().length < 3) e.name = 'Name must be at least 3 characters'
  if (form.sku.trim().length < 3) e.sku = 'SKU must be at least 3 characters'
  if (form.product_group_id <= 0) e.product_group_id = 'Please select a product group'
  if (!Number.isFinite(form.price) || form.price < 0) e.price = 'Price must be ≥ 0'
  if (!Number.isInteger(form.stock_qty) || form.stock_qty < 0)
    e.stock_qty = 'Stock must be an integer ≥ 0'

  clientFieldErrors.value = e
  return Object.keys(e).length === 0
}

//Clear form on succesfull submit
const form = reactive<ProductCreate>(defaults())
const submitted = ref(false)

//Variation Options add
function addVariationRow() {
  ;(form.options as any).push(makeVariationRow())
}

function removeVariationRow(i: number) {
  const rows = form.options as any as ProductVariation[]
  rows.splice(i, 1)
}

const variationStore = useVariationStore()

//Variation option error
const variationRowErrors = ref<Record<number, string>>({})

function validateVariationRows() {
  const rows = form.options as any as ProductVariation[]

  if (rows.length === 0) {
    variationRowErrors.value = {}
    return true
  }

  const counts = new Map<number, number>()
  rows.forEach((r) => {
    if (r.variation_id > 0) {
      counts.set(r.variation_id, (counts.get(r.variation_id) ?? 0) + 1)
    }
  })

  const errs: Record<number, string> = {}

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

//remove error when valid

watch(
  () => form.sku,
  (sku) => {
    if (clientFieldErrors.value.sku && sku.trim().length >= 3) {
      clientFieldErrors.value = { ...clientFieldErrors.value, sku: undefined }
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
  () => form.price,
  (price) => {
    if (clientFieldErrors.value.price && Number.isFinite(price) && price >= 0) {
      clientFieldErrors.value = { ...clientFieldErrors.value, price: undefined }
    }
  },
)

watch(
  () => form.stock_qty,
  (stock_qty) => {
    if (clientFieldErrors.value.stock_qty && Number.isInteger(stock_qty) && stock_qty >= 0) {
      clientFieldErrors.value = { ...clientFieldErrors.value, stock_qty: undefined }
    }
  },
)

watch(
  () => form.product_group_id,
  (productGroupId) => {
    if (clientFieldErrors.value.product_group_id && productGroupId > 0) {
      clientFieldErrors.value = { ...clientFieldErrors.value, product_group_id: undefined }
    }
  },
)

watch(
  () => (form.options as any as ProductVariation[]).map((r) => r.variation_id),
  () => {
    if (Object.keys(variationRowErrors.value).length) validateVariationRows()
  },
  { deep: true },
)

function onSubmit() {
  emit('clear-error')

  const validateFields = validate()
  const validateVariations = validateVariationRows()

  if (!validateFields || !validateVariations) {
    submitted.value = false
    return
  }

  const rows = form.options as any as ProductVariation[]
  const variationIds = rows.map((r) => r.variation_id)

  const payload = { ...form, options: variationIds }

  submitted.value = true
  emit('create', payload as any)
}

//Dropdown of product groups
const product_group_store = useProductGroupStore()

onMounted(() => {
  variationStore.fetchAll?.()
  product_group_store.fetchAll?.()
})
</script>

<template>
  <form @submit.prevent="onSubmit" class="card bg-base-100 shadow-xl max-w-2xl">
    <div class="card-body space-y-6">
      <header class="space-y-1">
        <h2 class="card-title text-2xl">Create product</h2>
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
            :class="clientFieldErrors.name || serverFieldErrors?.name ? 'input-error' : ''"
          >
            <input v-model="form.name" type="text" placeholder="e.g. Winter Jacket" class="" />
          </label>
          <label v-if="clientFieldErrors.name || serverFieldErrors?.name" class="label">
            <span class="label-text-alt text-error">{{
              clientFieldErrors.name || serverFieldErrors?.name
            }}</span>
          </label>
        </div>

        <!-- SKU -->
        <div class="form-control">
          <label class="label">
            <span class="label-text">SKU</span>
          </label>
          <label
            class="input input-bordered flex items-center gap-2"
            :class="clientFieldErrors.sku || serverFieldErrors?.sku ? 'input-error' : ''"
          >
            <input
              v-model="form.sku"
              type="text"
              placeholder="e.g. sku-iphone-16-white"
              class=""
              :class="clientFieldErrors.sku || serverFieldErrors?.sku ? 'input-error' : ''"
            />
          </label>
          <label v-if="clientFieldErrors.sku || serverFieldErrors?.sku" class="label">
            <span class="label-text-alt text-error">{{
              clientFieldErrors.sku || serverFieldErrors?.sku
            }}</span>
          </label>
        </div>

        <!-- Product group -->
        <div class="form-control">
          <label class="label">
            <span class="label-text">Product group</span>
          </label>

          <select
            v-model.number="form.product_group_id"
            class="select select-bordered w-full"
            :class="
              clientFieldErrors.product_group_id || serverFieldErrors?.product_group_id
                ? 'select-error'
                : ''
            "
            :disabled="submitting || product_group_store.loading"
          >
            <option disabled :value="0">Select a product group…</option>
            <option v-for="g in product_group_store.productGroups" :key="g.id" :value="g.id">
              {{ g.name }}
            </option>
          </select>

          <label
            v-if="clientFieldErrors.product_group_id || serverFieldErrors?.product_group_id"
            class="label"
          >
            <span class="label-text-alt text-error">{{
              clientFieldErrors.product_group_id || serverFieldErrors?.product_group_id
            }}</span>
          </label>

          <label v-if="product_group_store.error" class="label">
            <span class="label-text-alt text-error">{{ product_group_store.error }}</span>
          </label>
        </div>

        <!-- Price -->
        <div class="form-control">
          <label class="label">
            <span class="label-text">Price</span>
          </label>

          <label
            class="input input-bordered flex items-center gap-2"
            :class="clientFieldErrors.price || serverFieldErrors?.price ? 'input-error' : ''"
          >
            <span class="opacity-60">kr</span>
            <input
              v-model.number="form.price"
              type="number"
              step="1"
              placeholder="0.00"
              class="grow"
            />
          </label>

          <label v-if="clientFieldErrors.price || serverFieldErrors?.price" class="label">
            <span class="label-text-alt text-error">{{
              clientFieldErrors.price || serverFieldErrors?.price
            }}</span>
          </label>
        </div>

        <!-- Stock qty -->
        <div class="form-control">
          <label class="label">
            <span class="label-text">Stock quantity</span>
          </label>
          <input
            v-model.number="form.stock_qty"
            type="number"
            step="1"
            placeholder="0"
            class="input input-bordered w-full"
            :class="
              clientFieldErrors.stock_qty || serverFieldErrors?.stock_qty ? 'input-error' : ''
            "
          />
          <label v-if="clientFieldErrors.stock_qty || serverFieldErrors?.stock_qty" class="label">
            <span class="label-text-alt text-error">{{
              clientFieldErrors.stock_qty || serverFieldErrors?.stock_qty
            }}</span>
          </label>
        </div>

        <!-- Variations -->
        <div class="md:col-span-2 space-y-2">
          <div class="flex items-center justify-between">
            <label class="label p-0">
              <span class="label-text">Variations</span>
            </label>

            <button
              type="button"
              class="btn btn-outline btn-sm btn-square"
              @click="addVariationRow"
            >
              +
            </button>
          </div>

          <div class="space-y-2">
            <div
              v-for="(row, i) in form.options"
              :key="i"
              class="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-2 items-end"
            >
              <div class="form-control">
                <label class="label"><span class="label-text">Variation</span></label>

                <select
                  v-model.number="row.variation_id"
                  class="select select-bordered w-full"
                  :disabled="submitting || variationStore.loading"
                >
                  <option disabled :value="0">Select variation…</option>
                  <option v-for="v in variationStore.variations" :key="v.id" :value="v.id">
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

        <div class="hidden md:block"></div>

        <!-- Description -->
        <div class="form-control md:col-span-2">
          <label class="label">
            <span class="label-text">Description</span>
          </label>
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
          {{ submitting ? 'Saving…' : 'Create product' }}
        </button>
      </footer>
    </div>
  </form>
</template>
