<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useProductGroupStore } from '@/stores/admin/productGroup'
import { useVariationStore } from '@/stores/admin/variation'
import { useVariationOptionStore } from '@/stores/admin/variationOption'

const props = withDefaults(
  defineProps<{
    productGroupId: number
    modelValue: number[]
    disabled?: boolean
  }>(),
  {
    modelValue: () => [],
  },
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: number[]): void
}>()

const productGroupStore = useProductGroupStore()
const variationStore = useVariationStore()
const optionStore = useVariationOptionStore()

type Row = { variation_id: number; option_id: number }
const rows = ref<Row[]>([])
const rowErrors = ref<Record<number, string>>({})

const group = computed(() =>
  (productGroupStore.productGroups ?? []).find((g: any) => g.id === props.productGroupId),
)

const variationIds = computed<number[]>(() => (group.value?.variation_ids ?? []) as number[])

const variationName = (variation_id: number) =>
  (variationStore.variations ?? []).find((v: any) => v.id === variation_id)?.name ??
  `#${variation_id}`

const optionsForVariation = (variation_id: number) =>
  (optionStore.variationOptions ?? []).filter((o: any) => o.variation_id === variation_id)

function syncRowsFromModelValue() {
  if (!props.productGroupId || variationIds.value.length === 0) {
    rows.value = []
    rowErrors.value = {}
    return
  }
  const selectedByVariation = new Map<number, number>()
  for (const optionId of props.modelValue ?? []) {
    const opt = (optionStore.variationOptions ?? []).find((o: any) => o.id === optionId)
    if (opt) selectedByVariation.set(opt.variation_id, optionId)
  }

  rows.value = variationIds.value.map((vid) => ({
    variation_id: vid,
    option_id: selectedByVariation.get(vid) ?? 0,
  }))
}

function validate() {
  const errs: Record<number, string> = {}
  rows.value.forEach((r, i) => {
    if (r.option_id <= 0) errs[i] = 'Select an option'
  })
  rowErrors.value = errs
  return Object.keys(errs).length === 0
}

watch(
  () => props.productGroupId,
  async () => {
    if (!productGroupStore.productGroups?.length) await productGroupStore.fetchAll?.()
    if (!variationStore.variations?.length) await variationStore.fetchAll?.()
    if (!optionStore.variationOptions?.length) await optionStore.fetchAll?.()

    syncRowsFromModelValue()
  },
  { immediate: true },
)
function idsKey(ids: number[]) {
  return (ids ?? []).join(',')
}

function currentRowIds() {
  return rows.value.map((r) => r.option_id)
}

watch(
  () => props.modelValue,
  () => {
    const a = idsKey((props.modelValue ?? []) as number[])
    const b = idsKey(currentRowIds())
    if (a !== b) syncRowsFromModelValue()
  },
  { deep: false },
)

watch(
  () => idsKey(currentRowIds()),
  () => {
    const next = currentRowIds()
    const a = idsKey(next)
    const b = idsKey((props.modelValue ?? []) as number[])

    if (a !== b) {
      emit('update:modelValue', next)
    }

    if (Object.keys(rowErrors.value).length) validate()
  },
)



onMounted(async () => {
  await productGroupStore.fetchAll?.()
  await variationStore.fetchAll?.()
  await optionStore.fetchAll?.()
  syncRowsFromModelValue()
})
</script>

<template>
  <section class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold">Options</h3>
    </div>

    <div v-if="!productGroupId" class="text-sm opacity-70">
      Select a product group to choose options.
    </div>

    <div v-else-if="variationIds.length === 0" class="text-sm opacity-70">
      This product group has no variations.
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="(row, i) in rows"
        :key="row.variation_id"
        class="grid grid-cols-1 md:grid-cols-[1fr_2fr] gap-3 items-end"
      >
        <div class="font-medium">{{ variationName(row.variation_id) }}</div>

        <div class="form-control">
          <select
            v-model.number="row.option_id"
            class="select select-bordered w-full"
            :class="rowErrors[i] ? 'select-error' : ''"
            :disabled="disabled"
          >
            <option disabled :value="0">Select option…</option>
            <option v-for="o in optionsForVariation(row.variation_id)" :key="o.id" :value="o.id">
              {{ o.value }}
            </option>
          </select>

          <label v-if="rowErrors[i]" class="label">
            <span class="label-text-alt text-error">{{ rowErrors[i] }}</span>
          </label>
        </div>
      </div>
    </div>
  </section>
</template>
