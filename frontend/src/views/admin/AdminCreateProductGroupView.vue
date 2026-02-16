<script setup lang="ts">
import { ref } from 'vue'
import { useProductGroupStore } from '@/stores/admin/adminCreateProductGroup'

import AdminCreateProductGroupForm from '@/components/admin/AdminCreateProductGroupForm.vue'
import ProductGroupVariationsPicker from '@/components/admin/AdminCreateProductGroupAddVariations.vue'

const productGroupStore = useProductGroupStore()

const categoryId = ref(0)

const formRef = ref<InstanceType<typeof AdminCreateProductGroupForm> | null>(null)
const pickerRef = ref<InstanceType<typeof ProductGroupVariationsPicker> | null>(null)

function clearError() {
  productGroupStore.error = null
  productGroupStore.fieldErrors = {}
}

async function submitAll() {
  clearError()

  const okForm = formRef.value?.validate?.() ?? true
  const okPicker = pickerRef.value?.validate?.() ?? true
  if (!okForm || !okPicker) return

  const basics = formRef.value!.getPayload()
  const variation_ids = pickerRef.value?.getVariationIds?.() ?? []

  await productGroupStore.create({
    ...basics,
    variation_ids,
  } as any)
}
</script>

<template>
  <main class="p-4 space-y-6">
    <AdminCreateProductGroupForm
      ref="formRef"
      :submitting="productGroupStore.loading"
      :general-error="productGroupStore.error"
      :server-field-errors="productGroupStore.fieldErrors"
      :category-id="categoryId"
      @update:categoryId="categoryId = $event"
      @clear-error="clearError"
    />

    <ProductGroupVariationsPicker
      ref="pickerRef"
      :category-id="categoryId"
      :disabled="productGroupStore.loading"
    />

    <div class="card bg-base-100 shadow-xl max-w-3xl">
      <div class="card-body">
        <footer class="card-actions justify-end gap-2">
          <button type="button" class="btn btn-ghost" @click="$router.push('/')">Cancel</button>

          <button
            type="button"
            class="btn btn-primary"
            :disabled="productGroupStore.loading"
            @click="submitAll"
          >
            <span
              v-if="productGroupStore.loading"
              class="loading loading-spinner loading-sm"
            ></span>
            {{ productGroupStore.loading ? 'Saving…' : 'Create product group' }}
          </button>
        </footer>
      </div>
    </div>
  </main>
</template>
