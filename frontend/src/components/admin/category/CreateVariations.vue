<script setup lang="ts">
import { ref, computed, onMounted, watchEffect } from 'vue'
import type { VariationCreate } from '@/types/admin/variation'
import type { VariationOptionCreate } from '@/types/admin/variationOption'
import { useVariationStore } from '@/stores/admin/variation'
import { useVariationOptionStore } from '@/stores/admin/variationOption'

// PROPS & STORE

const props = defineProps<{
  categoryId?: number | null
  mode?: 'create' | 'update'
}>()

const variationStore = useVariationStore()
const variationOptionStore = useVariationOptionStore()

// COMPUTED
const mode = computed(() => props.mode ?? 'create')
const existingVariations = computed(() =>
  variationStore.variations.filter((v) => v.category_id === props.categoryId),
)
const optionsForVariation = (variationId: number) =>
  variationOptionStore.variationOptions.filter((o) => o.variation_id === variationId)

// TYPES
type DraftOption = Pick<VariationOptionCreate, 'value'>
type OptionErrorMap = Record<number, string>

interface BaseVariation {
  id?: number
  name: string
  saving: boolean
  error: string | null
  savedMsg: string | null
  newOptions: DraftOption[]
  newOptionErrors: OptionErrorMap
  savingNewOptions: boolean
}

interface DraftVariation extends BaseVariation {}

interface EditOption {
  id: number
  value: string
  saving: boolean
  error: string | null
}

interface EditVariation extends BaseVariation {
  id: number
  options: EditOption[]
}

// STATE
const drafts = ref<DraftVariation[]>([])
const editVariations = ref<EditVariation[]>([])

// HELPERS
function createDraftVariation(): DraftVariation {
  return {
    id: undefined,
    name: '',
    saving: false,
    error: null,
    savedMsg: null,
    newOptions: [{ value: '' }],
    newOptionErrors: {},
    savingNewOptions: false,
  }
}

function validateOptions(options: DraftOption[]): { isValid: boolean; errors: OptionErrorMap } {
  const errors: OptionErrorMap = {}
  const seen = new Map<string, number>()

  options.forEach((o, i) => {
    const val = o.value.trim()
    if (!val) errors[i] = 'Please enter a value'
    else if (val.length < 2) errors[i] = 'Must be at least 2 characters'
    else {
      const key = val.toLowerCase()
      if (seen.has(key)) {
        errors[i] = 'Duplicate value'
        errors[seen.get(key)!] = 'Duplicate value'
      } else {
        seen.set(key, i)
      }
    }
  })

  return { isValid: Object.keys(errors).length === 0, errors }
}

// ACTIONS
function addDraftVariation() {
  drafts.value.push(createDraftVariation())
}

function removeDraftVariation(i: number) {
  drafts.value.splice(i, 1)
}

function addOption(v: BaseVariation) {
  v.newOptions.push({ value: '' })
}

function removeOption(v: BaseVariation, i: number) {
  v.newOptions.splice(i, 1)
  const nextErrors: OptionErrorMap = {}
  v.newOptions.forEach((_, idx) => {
    if (v.newOptionErrors[idx]) nextErrors[idx] = v.newOptionErrors[idx]
  })
  v.newOptionErrors = nextErrors
}

async function saveVariation(v: BaseVariation) {
  v.error = null
  v.savedMsg = null

  if (!props.categoryId) return (v.error = 'Select a category first')
  if (v.name.trim().length < 2) return (v.error = 'Variation name must be at least 2 characters')

  v.saving = true
  try {
    if (v.id) {
      await variationStore.update(v.id, { name: v.name.trim() })
      v.savedMsg = 'Variation updated'
    } else {
      const payload: VariationCreate = { name: v.name.trim(), category_id: props.categoryId }
      const created = await variationStore.create(payload)
      if (!created?.id) throw new Error(variationStore.error ?? 'Failed to save variation')

      v.id = created.id
      v.savedMsg = 'Variation saved'
    }
  } catch (err: any) {
    v.error = err.message || 'Action failed'
  } finally {
    v.saving = false
  }
}

async function saveOptions(v: BaseVariation) {
  v.error = null
  v.savedMsg = null

  if (!v.id) return (v.error = 'Save the variation first')

  const { isValid, errors } = validateOptions(v.newOptions)
  v.newOptionErrors = errors
  if (!isValid) return

  const values = v.newOptions.map((o) => o.value.trim()).filter(Boolean)
  if (!values.length) return

  v.savingNewOptions = true
  try {
    for (const value of values) {
      const payload: VariationOptionCreate = { variation_id: v.id, value }
      const created = await variationOptionStore.create(payload)

      if (!created?.id) throw new Error(variationOptionStore.error ?? 'Failed to save options')

      if ('options' in v && Array.isArray((v as EditVariation).options)) {
        ;(v as EditVariation).options.push({
          id: created.id,
          value: created.value,
          saving: false,
          error: null,
        })
      }
    }

    v.savedMsg = 'Options saved'
    v.newOptions = [{ value: '' }]
    v.newOptionErrors = {}
  } catch (err: any) {
    v.error = err.message || 'Action failed'
  } finally {
    v.savingNewOptions = false
  }
}

async function updateExistingOption(o: EditOption) {
  o.saving = true
  o.error = null
  try {
    await variationOptionStore.update(o.id, { value: o.value.trim() })
  } catch {
    o.error = variationOptionStore.error ?? 'Failed to update option'
  } finally {
    o.saving = false
  }
}

// WATTCHERS
watchEffect(() => {
  if (mode.value !== 'update' || !props.categoryId) return

  editVariations.value = existingVariations.value.map((v) => ({
    id: v.id,
    name: v.name,
    saving: false,
    error: null,
    savedMsg: null,
    options: optionsForVariation(v.id).map((o) => ({
      id: o.id,
      value: o.value,
      saving: false,
      error: null,
    })),
    newOptions: [{ value: '' }],
    newOptionErrors: {},
    savingNewOptions: false,
  }))
})

onMounted(async () => {
  if (mode.value === 'update' && props.categoryId) {
    await Promise.all([variationStore.fetchAll(true), variationOptionStore.fetchAll(true)])
  }
})
</script>

<template>
  <div class="card bg-base-100 shadow-xl max-w-3xl">
    <div class="card-body space-y-6">
      <h3 class="card-title text-xl">Variations</h3>

      <div v-if="mode === 'update'" class="space-y-4">
        <div v-if="!categoryId" class="text-sm opacity-70">No category selected.</div>

        <div
          v-for="v in editVariations"
          :key="v.id"
          class="rounded-box border border-base-300 p-4 space-y-3"
        >
          <div class="flex gap-2 items-end">
            <div class="form-control flex-1">
              <label class="label"><span class="label-text">Variation name</span></label>
              <input v-model="v.name" class="input input-bordered w-full" />
            </div>
            <button class="btn btn-primary btn-sm" @click="saveVariation(v)" :disabled="v.saving">
              <span v-if="v.saving" class="loading loading-spinner loading-xs"></span>
              Update
            </button>
          </div>

          <div v-if="v.error" class="text-sm text-error">{{ v.error }}</div>
          <div v-else-if="v.savedMsg" class="text-sm text-success">{{ v.savedMsg }}</div>

          <div class="space-y-2">
            <div class="font-medium">Options</div>
            <div v-for="o in v.options" :key="o.id" class="flex gap-2 items-center">
              <input v-model="o.value" class="input input-bordered flex-1" />
              <button
                class="btn btn-secondary btn-sm"
                @click="updateExistingOption(o)"
                :disabled="o.saving"
              >
                <span v-if="o.saving" class="loading loading-spinner loading-xs"></span>
                Update
              </button>
            </div>
            <div v-if="v.options.length === 0" class="text-sm opacity-70">No options yet.</div>
          </div>

          <div class="mt-3 space-y-2">
            <div class="flex items-center justify-between">
              <div class="font-medium">Add new options</div>
              <button
                type="button"
                class="btn btn-outline btn-xs btn-square"
                @click="addOption(v)"
                :disabled="v.savingNewOptions"
                title="Add option"
              >
                +
              </button>
            </div>

            <div v-for="(no, ni) in v.newOptions" :key="ni" class="flex gap-2 items-start">
              <div class="form-control flex-1">
                <input
                  v-model="no.value"
                  class="input input-bordered w-full"
                  :class="v.newOptionErrors[ni] ? 'input-error' : ''"
                  placeholder="e.g. Blue"
                  :disabled="v.savingNewOptions"
                />
                <label v-if="v.newOptionErrors[ni]" class="label">
                  <span class="label-text-alt text-error">{{ v.newOptionErrors[ni] }}</span>
                </label>
              </div>
              <button
                type="button"
                class="btn btn-ghost btn-square"
                @click="removeOption(v, ni)"
                :disabled="v.savingNewOptions"
                title="Remove option"
              >
                ✕
              </button>
            </div>

            <button
              type="button"
              class="btn btn-secondary btn-sm"
              @click="saveOptions(v)"
              :disabled="v.savingNewOptions"
            >
              <span v-if="v.savingNewOptions" class="loading loading-spinner loading-xs"></span>
              Add options
            </button>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div class="font-medium">Add new variations</div>
          <button
            type="button"
            class="btn btn-outline btn-sm btn-square"
            @click="addDraftVariation"
            :disabled="!categoryId"
            title="Add variation"
          >
            +
          </button>
        </div>

        <div v-if="!categoryId" class="text-sm opacity-70">
          Select/create the category first, then you can add variations and options.
        </div>

        <div
          v-for="(v, vi) in drafts"
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
                :disabled="v.saving || v.savingNewOptions"
              />
            </div>

            <button
              type="button"
              class="btn btn-primary btn-sm"
              @click="saveVariation(v)"
              :disabled="!categoryId || v.saving || v.savingNewOptions"
            >
              <span v-if="v.saving" class="loading loading-spinner loading-xs"></span>
              {{ v.id ? 'Saved' : 'Save' }}
            </button>

            <button
              type="button"
              class="btn btn-ghost btn-sm btn-square"
              @click="removeDraftVariation(vi)"
              :disabled="v.saving || v.savingNewOptions"
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
                :disabled="!v.id || v.savingNewOptions || v.saving"
                title="Add option"
              >
                +
              </button>
            </div>

            <div v-if="!v.id" class="text-sm opacity-70">
              Save the variation first to add options.
            </div>

            <div v-for="(o, oi) in v.newOptions" :key="oi" class="flex gap-2 items-start">
              <div class="form-control flex-1">
                <input
                  v-model="o.value"
                  class="input input-bordered w-full"
                  :class="v.newOptionErrors[oi] ? 'input-error' : ''"
                  placeholder="e.g. Red"
                  :disabled="!v.id || v.savingNewOptions || v.saving"
                />
                <label v-if="v.newOptionErrors[oi]" class="label">
                  <span class="label-text-alt text-error">{{ v.newOptionErrors[oi] }}</span>
                </label>
              </div>

              <button
                type="button"
                class="btn btn-ghost btn-square"
                @click="removeOption(v, oi)"
                :disabled="!v.id || v.savingNewOptions || v.saving"
                title="Remove option"
              >
                ✕
              </button>
            </div>

            <button
              type="button"
              class="btn btn-secondary btn-sm"
              @click="saveOptions(v)"
              :disabled="!v.id || v.savingNewOptions || v.saving"
            >
              <span v-if="v.savingNewOptions" class="loading loading-spinner loading-xs"></span>
              Save options
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
