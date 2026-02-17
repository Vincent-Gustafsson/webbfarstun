<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useVariationStore } from '@/stores/admin/adminVariation'

const props = defineProps<{
  categoryId: number
  disabled?: boolean
  embedded?: boolean
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
  if (rows.value.length === 0) {
    rowErrors.value = {}
    return true
  }

  const errs: Record<number, string> = {}

  const idToName = new Map<number, string>()
  filteredVariations.value.forEach((v: any) => {
    idToName.set(
      v.id,
      String(v.name ?? '')
        .trim()
        .toLowerCase(),
    )
  })

  const countsById = new Map<number, number>()
  const countsByName = new Map<string, number>()

  rows.value.forEach((r) => {
    if (r.variation_id > 0) {
      countsById.set(r.variation_id, (countsById.get(r.variation_id) ?? 0) + 1)
      const nm = idToName.get(r.variation_id)
      if (nm) countsByName.set(nm, (countsByName.get(nm) ?? 0) + 1)
    }
  })

  rows.value.forEach((r, i) => {
    if (r.variation_id <= 0) {
      errs[i] = 'Please select a variation'
      return
    }

    if ((countsById.get(r.variation_id) ?? 0) > 1) {
      errs[i] = 'This variation is already selected'
      return
    }

    const nm = idToName.get(r.variation_id)
    if (nm && (countsByName.get(nm) ?? 0) > 1) {
      errs[i] = 'A variation with this name is already selected'
      return
    }
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

defineExpose({
  validate,
  getVariationIds,
})
</script>

<template>
  <div :class="embedded ? '' : 'card bg-base-100 shadow-xl max-w-3xl'">
    <div :class="embedded ? 'space-y-4' : 'card-body space-y-4'">
      <div class="flex items-center justify-between">
        <h3 v-if="!embedded" class="card-title text-xl">Variations</h3>

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
