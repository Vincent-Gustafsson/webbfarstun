<script setup lang="ts">
import { computed, onMounted, ref, watch, nextTick } from 'vue'
import { useProductGroupStore } from '@/stores/admin/productGroup'
import { useVariationStore } from '@/stores/admin/variation'
import { useVariationOptionStore } from '@/stores/admin/variationOption'

// PROPS & EMITS
interface Props {
  productGroupId: number
  modelValue: number[]
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
})
const emit = defineEmits<{
  (e: 'update:modelValue', value: number[]): void
}>()

// STORE & STATE

const productGroupStore = useProductGroupStore()
const variationStore = useVariationStore()
const optionStore = useVariationOptionStore()

type Row = { variation_id: number; option_id: number }
const rows = ref<Row[]>([])
const rowErrors = ref<Record<number, string>>({})

//COMPUTED DATA

const currentGroup = computed(() =>
  productGroupStore.productGroups?.find((g) => g.id === props.productGroupId),
)

const variationIds = computed<number[]>(() => (currentGroup.value?.variation_ids ?? []) as number[])

//UI HELPERS

const getVariationName = (vId: number) =>
  variationStore.variations?.find((v) => v.id === vId)?.name ?? `#${vId}`

const getOptionsForVariation = (vId: number) =>
  optionStore.variationOptions?.filter((o) => o.variation_id === vId) ?? []

//LOGIC
const syncRows = () => {
  if (!props.productGroupId || variationIds.value.length === 0) {
    rows.value = []
    return
  }

  rows.value = variationIds.value.map((vId) => {
    const existingOption = props.modelValue.find((optId) => {
      const opt = optionStore.variationOptions?.find((o) => o.id === optId)
      return opt?.variation_id === vId
    })
    return { variation_id: vId, option_id: existingOption ?? 0 }
  })
}

const validate = () => {
  const errs: Record<number, string> = {}
  rows.value.forEach((row, i) => {
    if (row.option_id <= 0) errs[i] = 'Select an option'
  })
  rowErrors.value = errs
  return Object.keys(errs).length === 0
}

//WATCHERS

watch(
  () => props.productGroupId,
  async (id) => {
    if (!id) return (rows.value = [])

    await Promise.all([
      productGroupStore.fetchAll?.(),
      variationStore.fetchAll?.(),
      optionStore.fetchAll?.(),
    ])

    await nextTick()
    syncRows()
  },
  { immediate: true },
)

watch(
  rows,
  (newRows) => {
    const ids = newRows.map((r) => r.option_id)

    if (JSON.stringify(ids) !== JSON.stringify(props.modelValue)) {
      emit('update:modelValue', ids)
    }

    if (Object.keys(rowErrors.value).length > 0) validate()
  },
  { deep: true },
)

onMounted(() => syncRows())
</script>

<template>
  <section class="space-y-4">
    <header class="flex items-center justify-between">
      <h3 class="text-lg font-semibold">Options</h3>
    </header>

    <div v-if="!productGroupId" class="text-sm opacity-70 italic">
      Select a product group to choose options.
    </div>

    <div v-else-if="variationIds.length === 0" class="text-sm opacity-70 italic">
      This product group has no variations.
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="(row, i) in rows"
        :key="row.variation_id"
        class="grid grid-cols-1 md:grid-cols-[1fr_2fr] gap-3 items-center border-b border-base-200 pb-3 last:border-0"
      >
        <label class="font-medium text-sm">{{ getVariationName(row.variation_id) }}</label>

        <div class="form-control w-full">
          <select
            v-model.number="row.option_id"
            class="select select-bordered select-sm md:select-md w-full"
            :class="{ 'select-error': rowErrors[i] }"
            :disabled="disabled"
          >
            <option :value="0" disabled>Select option…</option>
            <option
              v-for="opt in getOptionsForVariation(row.variation_id)"
              :key="opt.id"
              :value="opt.id"
            >
              {{ opt.value }}
            </option>
          </select>

          <label v-if="rowErrors[i]" class="label py-1">
            <span class="label-text-alt text-error text-xs">{{ rowErrors[i] }}</span>
          </label>
        </div>
      </div>
    </div>
  </section>
</template>
