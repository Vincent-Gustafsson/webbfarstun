<script setup lang="ts">
import { ref } from 'vue'
import AdminCreateProductForm from '@/components/admin/product/Form.vue'
import AdminCreateProductVariationOptionsPicker from '@/components/admin/product/Create.vue'
import { useProductStore } from '@/stores/admin/product'
import AdminCreateProductImage from '@/components/admin/product/CreateImage.vue'

const productStore = useProductStore()

const productGroupId = ref(0)
const optionIds = ref<number[]>([])

function clearError() {
  productStore.error = null
  productStore.fieldErrors = {}
}
</script>

<template>
  <main class="p-4">
    <AdminCreateProductForm
      v-model:product-group-id="productGroupId"
      :variation-option-ids="optionIds"
      :submitting="productStore.loading"
      :general-error="productStore.error"
      :server-field-errors="productStore.fieldErrors"
      @clear-error="clearError"
      @create="productStore.create"
      @cancel="$router.push('/')"
    >
      <template #options>
        <div class="divider my-2"></div>

        <AdminCreateProductVariationOptionsPicker
          v-model="optionIds"
          :product-group-id="productGroupId"
          :disabled="productStore.loading"
        />
      </template>
    </AdminCreateProductForm>

    <div class="divider my-2"></div>

    <div v-if="!productStore.createdId" class="text-sm opacity-70">
      Create the product first, then you can upload images.
    </div>

    <AdminCreateProductImage
      v-else
      :product-id="productStore.createdId"
      :disabled="productStore.loading"
    />
  </main>
</template>
