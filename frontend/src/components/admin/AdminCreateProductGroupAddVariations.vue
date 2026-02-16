<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useVariationStore } from '@/stores/admin/adminVariation'

const props = defineProps<{
  categoryId: number
  disabled?: boolean
}>()

type VariationRow = { variation_id: number }
const makeVariationRow = (): VariationRow => ({ variation_id: 0 })

const variationStore = useVariationStore()

const rows = ref<VariationRow[]>([])
const rowErrors = ref<Record<number, string>>({})

const filteredVariations = computed(() => {
  if (!props.categoryId) return []
  return (variationStore.variations ?? []).filter((v: any) => v.category_id === props.categoryId)
})

function addRow() {
  rows.value.push(makeVariationRow())
}

function removeRow(i: number) {
  rows.value.splice(i, 1)
  validate()
}

function validate() {
  // variations are OPTIONAL
  if (rows.value.length === 0) {
    rowErrors.value = {}
    return true
  }

  const errs: Record<number, string> = {}

  const counts = new Map<number, number>()
  rows.value.forEach((r) => {
    if (r.variation_id > 0) counts.set(r.variation_id, (counts.get(r.variation_id) ?? 0) + 1)
  })

  rows.value.forEach((r, i) => {
    if (r.variation_id <= 0) errs[i] = 'Please select a variation'
    else if ((counts.get(r.variation_id) ?? 0) > 1) errs[i] = 'This variation is already selected'
  })

  rowErrors.value = errs
  return Object.keys(errs).length === 0
}

function getVariationIds() {
  return rows.value.map((r) => r.variation_id).filter((id) => id > 0)
}

// reset when category changes
watch(
  () => props.categoryId,
  () => {
    rows.value = []
    rowErrors.value = {}
  },
)

watch(
  () => rows.value.map((r) => r.variation_id),
  () => {
    if (Object.keys(rowErrors.value).length) validate()
  },
  { deep: true },
)

onMounted(() => {
  variationStore.fetchAll?.()
})

// parent can call these on submit
defineExpose({
  validate,
  getVariationIds,
})
</script>

<template>
  <div class="card bg-base-100 shadow-xl max-w-3xl">
    <div class="card-body space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="card-title text-xl">Variations</h3>

        <button
          type="button"
          class="btn btn-outline btn-sm btn-square"
          @click="addRow"
          :disabled="disabled || !categoryId"
          title="Add variation"
        >
          +
        </button>
      </div>

      <div v-if="!categoryId" class="text-sm opacity-70">
        Select a category first to choose variations.
      </div>

      <div v-else-if="filteredVariations.length === 0" class="text-sm opacity-70">
        This category has no variations.
      </div>

      <div v-else-if="rows.length === 0" class="text-sm opacity-70">
        No variations added (optional). Click + to add.
      </div>

      <div class="space-y-2">
        <div
          v-for="(row, i) in rows"
          :key="i"
          class="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-2 items-end"
        >
          <div class="form-control">
            <label class="label"><span class="label-text">Variation</span></label>

            <select
              v-model.number="row.variation_id"
              class="select select-bordered w-full"
              :class="rowErrors[i] ? 'select-error' : ''"
              :disabled="disabled"
            >
              <option disabled :value="0">Select variation…</option>
              <option v-for="v in filteredVariations" :key="v.id" :value="v.id">
                {{ v.name }}
              </option>
            </select>

            <label v-if="rowErrors[i]" class="label">
              <span class="label-text-alt text-error">{{ rowErrors[i] }}</span>
            </label>
          </div>

          <button
            type="button"
            class="btn btn-ghost btn-square"
            @click="removeRow(i)"
            :disabled="disabled"
            title="Remove"
          >
            ✕
          </button>
        </div>
      </div>

      <label v-if="variationStore.error" class="label">
        <span class="label-text-alt text-error">{{ variationStore.error }}</span>
      </label>
    </div>
  </div>
</template>
