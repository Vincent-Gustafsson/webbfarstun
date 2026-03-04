<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProductGroupStore } from '@/stores/admin/productGroup'
import AdminProductGroupUpdate from '@/components/admin/productGroup/Update.vue'

const props = defineProps<{ product_group_id: string | number }>()
const router = useRouter()
const productGroupStore = useProductGroupStore()

const productGroupId = computed(() => Number(props.product_group_id))

function clearProductGroupError() {
  productGroupStore.error = null
  productGroupStore.fieldErrors = {}
}

onMounted(async () => {
  const id = productGroupId.value
  if (!Number.isFinite(id)) return

  await productGroupStore.fetchOne(id)
})
</script>

<template>
  <AdminProductGroupUpdate
    v-if="productGroupId > 0"
    :id="productGroupId"
    :submitting="productGroupStore.loading"
    :general-error="productGroupStore.error"
    :server-field-errors="productGroupStore.fieldErrors"
    @clear-error="clearProductGroupError"
    @cancel="router.push('/admin/list/product-groups')"
    @update="(payload) => productGroupStore.update(productGroupId, payload)"
  />
</template>
