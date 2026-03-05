<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useProductStore } from '@/stores/products'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'

import ProductInformation from '@/components/ProductInformation.vue'
import ProductReviews from '@/components/ProductReviews.vue'

import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

const users = useUserStore()

const props = defineProps<{ id: string }>()
const productStore = useProductStore()
const { activeProduct, loading, error, availability } = storeToRefs(productStore)

const cartStore = useCartStore()
async function handleAddToCart() {
  if (!activeProduct.value || !isCompleteSelection()) return

  try {
    await cartStore.addToCart({
      product_id: activeProduct.value.id,
      qty: 1, // You could also add a 'quantity' ref to the UI if needed
    })
  } catch (err) {}
}

// local selection: variation_id -> option_id|null
const selectedByVariation = ref<Record<number, number | null>>({})

function selectedOptionIds() {
  return Object.values(selectedByVariation.value).filter((x): x is number => x != null)
}

function isCompleteSelection() {
  const vars = activeProduct.value?.variations ?? []
  return vars.length > 0 && vars.every((v: any) => selectedByVariation.value[v.id] != null)
}

function isAvailable(optionId: number) {
  // before first availability fetch, treat as available
  const v = availability.value[optionId]
  return v === undefined ? true : v
}

async function refreshAvailability() {
  const p = activeProduct.value
  if (!p) return
  await productStore.fetchAvailability(p.product_group_id, selectedOptionIds())

  // if current selection became invalid due to another change, clear it
  for (const v of p.variations as any[]) {
    const picked = selectedByVariation.value[v.id]
    if (picked != null && !isAvailable(picked)) {
      selectedByVariation.value[v.id] = null
    }
  }
}

async function maybeResolveAndLoad() {
  const p = activeProduct.value
  if (!p) return
  if (!isCompleteSelection()) return

  const res = await productStore.resolveVariantProduct(p.product_group_id, selectedOptionIds())
  if (!res?.product_id) return

  const currentId = Number(route.params.id)
  if (currentId === res.product_id) return

  // Update URL (replace avoids polluting history)
  await router.replace({
    name: route.name as string, // assumes you have a named route for product page
    params: { ...route.params, id: String(res.product_id) },
    query: route.query,
  })
}

async function selectOption(variationId: number, optionId: number) {
  selectedByVariation.value[variationId] = optionId
  await refreshAvailability()
  await maybeResolveAndLoad()
}

async function load() {
  const id = Number(props.id)
  if (!Number.isFinite(id)) return
  await productStore.fetchOne(id)
}

onMounted(load)
watch(() => props.id, load)

// When activeProduct changes (initial load or after resolve), initialize selection then fetch availability
watch(
  () => activeProduct.value,
  async (p) => {
    if (!p) return
    // Initialize selection from the currently loaded product if your API provides it:
    // expects p.variations[].selected_option_id
    const init: Record<number, number | null> = {}
    for (const v of p.variations as any[]) init[v.id] = v.selected_option_id ?? null
    selectedByVariation.value = init

    await refreshAvailability()
  },
  { immediate: true },
)
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

    <div class="flex-1 card bg-base-100 shadow p-4 gap-4">
      <div v-for="v in activeProduct.variations" :key="v.id" class="form-control w-full max-w-xs">
        <label class="label">
          <span class="label-text">{{ v.name }}</span>
        </label>

        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="opt in v.options"
            :key="opt.id"
            type="button"
            class="btn w-full"
            :disabled="!isAvailable(opt.id)"
            :class="[
              selectedByVariation[v.id] === opt.id ? 'btn-secondary' : 'btn-outline',
              !isAvailable(opt.id) ? 'opacity-50 line-through' : '',
            ]"
            @click="selectOption(v.id, opt.id)"
          >
            {{ opt.value }}
          </button>
        </div>

        <div v-if="selectedByVariation[v.id] == null" class="text-xs opacity-70 mt-2">
          Choose {{ v.name }}
        </div>
      </div>

      <div class="divider"></div>
      <h2 class="text-4xl text-center">{{ activeProduct.price }} kr</h2>
      <div class="divider"></div>

      <div
        class="tooltip"
        :data-tip="users.isLoggedIn ? '' : 'You must be logged in to write a review'"
      >
        <button
          class="btn btn-accent w-full"
          :disabled="!isCompleteSelection() || !users.isLoggedIn"
          @click="handleAddToCart"
        >
          Add to cart
        </button>
      </div>
    </div>
  </div>
</template>
