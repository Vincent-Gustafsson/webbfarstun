<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useProductStore } from '@/stores/products'
import ProductInformation from '@/components/ProductInformation.vue'
import ProductReviews from '@/components/ProductReviews.vue'

const props = defineProps<{ id: string }>() // if your route uses props: true

const productStore = useProductStore()
const { activeProduct, loading, error } = storeToRefs(productStore)

async function load() {
  const id = Number(props.id)
  if (!Number.isFinite(id)) return
  await productStore.fetchOne(id)
}

onMounted(load)
watch(() => props.id, load)
</script>

<template>
  <div v-if="loading" class="skeleton h-32 w-full"></div>

  <div v-else-if="error" class="alert alert-error">
    <span>{{ error }}</span>
  </div>

  <div v-else-if="activeProduct" class="flex gap-4">
    <div class="flex flex-col gap-4 flex-3">
      <ProductInformation />
      <ProductReviews />
    </div>

    <div class="flex-1 card bg-base-100 shadow p-4">
      <h2 class="text-4xl text-accent text-center">(Options)</h2>
      <div class="divider"></div>
      <h2 class="text-4xl text-center">{{ activeProduct.price }} kr</h2>
      <div class="divider"></div>
      <button class="btn btn-secondary" type="button" @click.stop>
        <svg xmlns="http://www.w3.org/2000/svg" fill="white" class="size-5" viewBox="0 0 640 512">
          <path
            d="M24-16C10.7-16 0-5.3 0 8S10.7 32 24 32l45.3 0c3.9 0 7.2 2.8 7.9 6.6l52.1 286.3c6.2 34.2 36 59.1 70.8 59.1L456 384c13.3 0 24-10.7 24-24s-10.7-24-24-24l-255.9 0c-11.6 0-21.5-8.3-23.6-19.7l-5.1-28.3 303.6 0c30.8 0 57.2-21.9 62.9-52.2L568.9 69.9C572.6 50.2 557.5 32 537.4 32l-412.7 0-.4-2c-4.8-26.6-28-46-55.1-46L24-16zM208 512a48 48 0 1 0 0-96 48 48 0 1 0 0 96zm224 0a48 48 0 1 0 0-96 48 48 0 1 0 0 96z"
          />
        </svg>
        Lägg i kundvagn
      </button>
    </div>
  </div>

  <!--
  <div v-if="loading" class="skeleton h-32 w-full"></div>

  <div v-else-if="error" class="alert alert-error">
    <span>{{ error }}</span>
  </div>

  <div v-else-if="activeProduct" class="card bg-base-100 shadow">
    <div class="card-body">
      <h1 class="card-title">{{ activeProduct.name }}</h1>
      <div class="text-lg font-semibold">{{ activeProduct.price }} kr</div>
      <div class="flex items-center gap-2">
        <div
          class="w-2 h-2 rounded-full"
          :class="activeProduct.stock_qty > 0 ? 'bg-success' : 'bg-error'"
        />
        <span>{{ activeProduct.stock_qty }} st</span>
      </div>

      <div class="card-actions justify-end mt-4">
        <button class="btn btn-secondary" type="button">Lägg i kundvagn</button>
      </div>
    </div>
  </div>
  -->
</template>
