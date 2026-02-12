<script setup lang="ts">
import { reactive, watch, computed, onMounted, ref } from 'vue'
import type { ProductCreate } from '@/types/adminCreateProduct'
import { useProductGroupStore } from '@/stores/productGroup'

const props = defineProps<{
  submitting?: boolean
  error?: string | null
}>()

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
  options: [],
})

//Clear form on succesfull submit
const form = reactive<ProductCreate>(defaults())
const submitted = ref(false)

function resetForm() {
  Object.assign(form, defaults())
  skuError.value = null
}

watch(
  () => props.submitting,
  (now, prev) => {
    if (prev && !now && submitted.value) {
      if (!props.error) resetForm()
      submitted.value = false
    }
  },
)

//Cast error on SKU != uniq
const skuError = ref<string | null>(null)
const generalError = computed(() => (skuError.value ? null : props.error))

watch(
  () => form.sku,
  (sku) => {
    emit('clear-error')

    if (!sku.trim()) {
      skuError.value = 'SKU cannot be empty'
      return
    }

    skuError.value = null
  },
)

//remove error when price or qty is >=0 or when product_group_id not set
watch(
  () => form.price,
  (price) => {
    if (fieldValueErrors.value.price && Number.isFinite(price) && price >= 0) {
      fieldValueErrors.value = { ...fieldValueErrors.value, price: undefined }
    }
  },
)

watch(
  () => form.stock_qty,
  (stock_qty) => {
    if (fieldValueErrors.value.stock_qty && Number.isInteger(stock_qty) && stock_qty >= 0) {
      fieldValueErrors.value = { ...fieldValueErrors.value, stock_qty: undefined }
    }
  },
)

watch(
  () => form.product_group_id,
  (productGroupId) => {
    if (fieldValueErrors.value.product_group_id && productGroupId > 0) {
      fieldValueErrors.value = { ...fieldValueErrors.value, product_group_id: undefined }
    }
  },
)

//Cast error if it isnt sku error
watch(
  () => props.error,
  (msg) => {
    if (!msg) {
      skuError.value = null
      return
    }
    if (msg.toLowerCase().includes('sku')) skuError.value = msg
  },
)

//validate value of price and stock_qty
const fieldValueErrors = ref<{ price?: string; stock_qty?: string; product_group_id?: string }>({})

function validate() {
  const e: typeof fieldValueErrors.value = {}

  if (form.product_group_id <= 0) e.product_group_id = 'Please select a product group'
  if (!Number.isFinite(form.price) || form.price < 0) e.price = 'Price must be ≥ 0'
  if (!Number.isInteger(form.stock_qty) || form.stock_qty < 0)
    e.stock_qty = 'Stock must be an integer ≥ 0'

  fieldValueErrors.value = e
  return Object.keys(e).length === 0
}

function onSubmit() {
  emit('clear-error')

  if (!form.sku.trim()) {
    skuError.value = 'SKU cannot be empty'
    submitted.value = false
    return
  }

  if (!validate()) {
    submitted.value = false
    return
  }

  submitted.value = true
  skuError.value = null

  emit('create', { ...form, sku: form.sku.trim() })
}

//Dropdown of product groups
const product_group_store = useProductGroupStore()

onMounted(() => {
  if (product_group_store.productGroups?.length) return
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
          <input
            v-model="form.name"
            type="text"
            placeholder="e.g. Winter Jacket"
            class="input input-bordered w-full"
          />
        </div>

        <!-- SKU -->
        <div class="form-control">
          <label class="label">
            <span class="label-text">SKU</span>
          </label>

          <input
            v-model="form.sku"
            type="text"
            placeholder="e.g. sku-iphone-16-white"
            class="input input-bordered w-full"
            :class="skuError ? 'input-error' : ''"
          />

          <label v-if="skuError" class="label">
            <span class="label-text-alt text-error">{{ skuError }}</span>
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
            :class="fieldValueErrors.product_group_id ? 'select-error' : ''"
            :disabled="submitting || product_group_store.loading"
          >
            <option disabled :value="0">Select a product group…</option>
            <option v-for="g in product_group_store.productGroups" :key="g.id" :value="g.id">
              {{ g.name }}
            </option>
          </select>

          <label v-if="fieldValueErrors.product_group_id" class="label">
            <span class="label-text-alt text-error">{{ fieldValueErrors.product_group_id }}</span>
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
            :class="fieldValueErrors.price ? 'input-error' : ''"
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

          <label v-if="fieldValueErrors.price" class="label">
            <span class="label-text-alt text-error">{{ fieldValueErrors.price }}</span>
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
            :class="fieldValueErrors.stock_qty ? 'input-error' : ''"
          />
          <label v-if="fieldValueErrors.stock_qty" class="label">
            <span class="label-text-alt text-error">{{ fieldValueErrors.stock_qty }}</span>
          </label>
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
