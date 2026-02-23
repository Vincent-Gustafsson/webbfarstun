<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '@/stores/admin/adminCreateProduct'

import AdminCreateProductForm from '@/components/admin/AdminCreateProductForm.vue'
//import AdminCreateProductVariations from '@/components/admin/AdminCreateProductAndVariationOptionsPicker.vue'

const props = defineProps<{ product_id: string | number }>()
const router = useRouter()

const productStore = useProductStore()

const productId = computed(() => Number(props.product_id))


onMounted(async () => {
  const id = productId.value
  if (!Number.isFinite(id)) {
    console.error('Invalid product_id prop:', props.product_id)
    return
  }
  await productStore.fetchOne(id)
})
</script>

<template>
  <AdminCreateProductForm
    mode="update"
    :product="productStore.current"
    :submitting="productStore.loading"
    :general-error="productStore.error"
    :server-field-errors="productStore.fieldErrors"
    @cancel="router.push('/admin/list/products')"
    @update="
      (payload) => {
        const id = productId
        if (!Number.isFinite(id)) {
          console.error('Invalid productId in submit:', id, 'raw:', props.product_id)
          return
        }
        productStore.update(id, payload)
      }
    "
  />
</template>
