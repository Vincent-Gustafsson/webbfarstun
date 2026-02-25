<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '@/stores/admin/adminCreateProduct'

import AdminCreateProductForm from '@/components/admin/AdminCreateProductForm.vue'
import AdminCreateProductVariationsOptionsPicker from '@/components/admin/AdminCreateProductAndVariationOptionsPicker.vue'
import AdminCreateProductImage from '@/components/admin/AdminCreateProductImage.vue'

const productStore = useProductStore()

const props = defineProps<{ product_id: string | number }>()
const router = useRouter()

const productId = computed(() => Number(props.product_id))

const productGroupId = ref(0)
const optionIds = ref<number[]>([])

watch(
  () => productStore.current,
  (p: any) => {
    if (!p) return

    const nextGroupId = Number(p.product_group_id ?? 0)

    const nextOptionIds = Array.isArray(p.options)
      ? p.options
          .map((x: any) => (typeof x === 'number' ? x : x?.id))
          .filter((x: any) => Number(x) > 0)
          .map((x: any) => Number(x))
      : []

    if (productGroupId.value !== nextGroupId) productGroupId.value = nextGroupId
    if (optionIds.value.join(',') !== nextOptionIds.join(',')) optionIds.value = nextOptionIds
  },
  { immediate: true },
)

function clearError() {
  productStore.error = null
  productStore.fieldErrors = {}
}

function submitUpdate(payload: any) {
  const id = productId.value
  if (!Number.isFinite(id)) {
    console.error('Invalid productId in submit:', id, 'raw:', props.product_id)
    return
  }

  productStore.update(id, {
    ...payload,
    options: optionIds.value,
  })
}

onMounted(async () => {
  const id = productId.value
  if (!Number.isFinite(id)) return
  await productStore.fetchOne(id)
})
</script>

<template>
  <AdminCreateProductForm
    v-model:product-group-id="productGroupId"
    :variation-option-ids="optionIds"
    mode="update"
    :product="productStore.current"
    :submitting="productStore.loading"
    :general-error="productStore.error"
    :server-field-errors="productStore.fieldErrors"
    @clear-error="clearError"
    @cancel="router.push('/admin/list/products')"
    @update="submitUpdate"
  >
    <template #options>
      <div class="divider my-2"></div>

      <AdminCreateProductVariationsOptionsPicker
        v-model="optionIds"
        :product-group-id="productGroupId"
        :disabled="productStore.loading"
      />
    </template>
  </AdminCreateProductForm>
  <div class="divider my-2"></div>
  <AdminCreateProductImage
    v-if="Number.isFinite(productId)"
    :product-id="productId"
    :disabled="productStore.loading"
  />
</template>
