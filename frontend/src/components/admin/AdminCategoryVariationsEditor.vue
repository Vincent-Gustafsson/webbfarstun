<script setup lang="ts">
import { ref } from 'vue'
import type { VariationCreate } from '@/types/admin/adminVariation'
import type { VariationOptionCreate } from '@/types/admin/adminVariationOption'
import { useVariationStore } from '@/stores/admin/adminVariation'
import { useVariationOptionStore } from '@/stores/admin/adminVariationOption'

const props = defineProps<{
  categoryId?: number | null
}>()

type DraftOption = Pick<VariationOptionCreate, 'value'>

type DraftVariation = Omit<VariationCreate, 'category_id'> & {
  id?: number
  savingVariation: boolean
  savingOptions: boolean
  error: string | null
  savedMsg: string | null
  optionErrors: Record<number, string>
  options: DraftOption[]
}

const makeDraftVariation = (): DraftVariation => ({
  id: undefined,
  name: '',
  savingVariation: false,
  savingOptions: false,
  error: null,
  savedMsg: null,
  options: [{ value: '' }],
  optionErrors: {},
})

const variations = ref<DraftVariation[]>([])

function addVariation() {
  variations.value.push(makeDraftVariation())
}

function removeVariation(i: number) {
  variations.value.splice(i, 1)
}

function addOption(v: DraftVariation) {
  v.options.push({ value: '' })
}

function removeOption(v: DraftVariation, i: number) {
  v.options.splice(i, 1)
  const next: Record<number, string> = {}
  v.options.forEach((_, idx) => {
    if (v.optionErrors[idx]) next[idx] = v.optionErrors[idx]
  })
  v.optionErrors = next
}

const variationStore = useVariationStore()
const variationOptionStore = useVariationOptionStore()

async function saveVariation(v: DraftVariation) {
  v.error = null
  v.savedMsg = null

  if (!props.categoryId) return (v.error = 'Create the category first')
  if (v.name.trim().length < 2) return (v.error = 'Variation name must be at least 2 characters')

  v.savingVariation = true
  try {
    const payload: VariationCreate = {
      name: v.name.trim(),
      category_id: props.categoryId,
    }

    const created = await variationStore.create(payload)
    if (!created?.id) {
      v.error = variationStore.error ?? 'Failed to save variation'
      return
    }

    v.id = created.id
    v.savedMsg = 'Variation saved'
  } finally {
    v.savingVariation = false
  }
}

function validateOptions(v: DraftVariation) {
  const errs: Record<number, string> = {}

  v.options.forEach((o, i) => {
    const val = o.value.trim()
    if (!val) errs[i] = 'Please enter a value'
    else if (val.length < 2) errs[i] = 'Must be at least 2 characters'
  })

  const seen = new Map<string, number>()
  v.options.forEach((o, i) => {
    const key = o.value.trim().toLowerCase()
    if (!key) return
    if (seen.has(key)) {
      errs[i] = 'Duplicate value'
      errs[seen.get(key)!] = 'Duplicate value'
    } else {
      seen.set(key, i)
    }
  })

  v.optionErrors = errs
  return Object.keys(errs).length === 0
}

async function saveOptions(v: DraftVariation) {
  v.error = null
  v.savedMsg = null

  if (!v.id) return (v.error = 'Save the variation first')
  if (!validateOptions(v)) return

  const values = v.options.map((o) => o.value.trim()).filter(Boolean)

  v.savingOptions = true
  try {
    for (const value of values) {
      const payload: VariationOptionCreate = { variation_id: v.id, value }
      const created = await variationOptionStore.create(payload)

      if (!created?.id) {
        v.error = variationOptionStore.error ?? 'Failed to save options'
        return
      }
    }

    v.savedMsg = 'Options saved'
    v.options = [{ value: '' }]
    v.optionErrors = {}
  } finally {
    v.savingOptions = false
  }
}
</script>

<template>
  <div class="card bg-base-100 shadow-xl max-w-3xl">
    <div class="card-body space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="card-title text-xl">Variations</h3>
        <button
          type="button"
          class="btn btn-outline btn-sm btn-square"
          @click="addVariation"
          :disabled="!categoryId"
          title="Add variation"
        >
          +
        </button>
      </div>

      <div v-if="!categoryId" class="text-sm opacity-70">
        Create the category first, then you can add variations and options.
      </div>

      <div
        v-for="(v, vi) in variations"
        :key="vi"
        class="rounded-box border border-base-300 p-4 space-y-3"
      >
        <div class="flex gap-2 items-end">
          <div class="form-control flex-1">
            <label class="label"><span class="label-text">Variation name</span></label>
            <input
              v-model="v.name"
              class="input input-bordered w-full"
              placeholder="e.g. Color"
              :disabled="v.savingVariation || v.savingOptions"
            />
          </div>

          <button
            type="button"
            class="btn btn-primary btn-sm"
            @click="saveVariation(v)"
            :disabled="!categoryId || v.savingVariation || v.savingOptions"
          >
            <span v-if="v.savingVariation" class="loading loading-spinner loading-xs"></span>
            {{ v.id ? 'Saved' : 'Save' }}
          </button>

          <button
            type="button"
            class="btn btn-ghost btn-sm btn-square"
            @click="removeVariation(vi)"
            :disabled="v.savingVariation || v.savingOptions"
            title="Remove variation"
          >
            ✕
          </button>
        </div>

        <div v-if="v.error" class="text-sm text-error">{{ v.error }}</div>
        <div v-else-if="v.savedMsg" class="text-sm text-success">{{ v.savedMsg }}</div>

        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <div class="font-medium">Options</div>
            <button
              type="button"
              class="btn btn-outline btn-xs btn-square"
              @click="addOption(v)"
              :disabled="!v.id || v.savingOptions || v.savingVariation"
              title="Add option"
            >
              +
            </button>
          </div>

          <div v-if="!v.id" class="text-sm opacity-70">
            Save the variation first to add options.
          </div>

          <div v-for="(o, oi) in v.options" :key="oi" class="flex gap-2 items-start">
            <div class="form-control flex-1">
              <input
                v-model="o.value"
                class="input input-bordered w-full"
                :class="v.optionErrors[oi] ? 'input-error' : ''"
                placeholder="e.g. Red"
                :disabled="!v.id || v.savingOptions || v.savingVariation"
              />
              <label v-if="v.optionErrors[oi]" class="label">
                <span class="label-text-alt text-error">{{ v.optionErrors[oi] }}</span>
              </label>
            </div>

            <button
              type="button"
              class="btn btn-ghost btn-square"
              @click="removeOption(v, oi)"
              :disabled="!v.id || v.savingOptions || v.savingVariation"
              title="Remove option"
            >
              ✕
            </button>
          </div>

          <button
            type="button"
            class="btn btn-secondary btn-sm"
            @click="saveOptions(v)"
            :disabled="!v.id || v.savingOptions || v.savingVariation"
          >
            <span v-if="v.savingOptions" class="loading loading-spinner loading-xs"></span>
            Save options
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
