<script setup lang="ts">
import { ref, computed, onMounted, watchEffect } from 'vue'
import type { VariationCreate } from '@/types/admin/adminVariation'
import type { VariationOptionCreate } from '@/types/admin/adminVariationOption'
import { useVariationStore } from '@/stores/admin/adminVariation'
import { useVariationOptionStore } from '@/stores/admin/adminVariationOption'

const props = defineProps<{
  categoryId?: number | null
  mode?: 'create' | 'update'
}>()

const variationStore = useVariationStore()
const variationOptionStore = useVariationOptionStore()
const mode = computed(() => props.mode ?? 'create')


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

const drafts = ref<DraftVariation[]>([])

function addDraftVariation() {
  drafts.value.push(makeDraftVariation())
}

function removeDraftVariation(i: number) {
  drafts.value.splice(i, 1)
}

function addDraftOption(v: DraftVariation) {
  v.options.push({ value: '' })
}

function removeDraftOption(v: DraftVariation, i: number) {
  v.options.splice(i, 1)
  const next: Record<number, string> = {}
  v.options.forEach((_, idx) => {
    if (v.optionErrors[idx]) next[idx] = v.optionErrors[idx]
  })
  v.optionErrors = next
}

async function saveDraftVariation(v: DraftVariation) {
  v.error = null
  v.savedMsg = null

  if (!props.categoryId) return (v.error = 'Select a category first')
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

function validateDraftOptions(v: DraftVariation) {
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

async function saveDraftOptions(v: DraftVariation) {
  v.error = null
  v.savedMsg = null

  if (!v.id) return (v.error = 'Save the variation first')
  if (!validateDraftOptions(v)) return

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


const existingVariations = computed(() =>
  variationStore.variations.filter((v) => v.category_id === props.categoryId),
)

const optionsForVariation = (variationId: number) =>
  variationOptionStore.variationOptions.filter((o) => o.variation_id === variationId)

type EditOption = { id: number; value: string; saving: boolean; error: string | null }

type EditVariation = {
  id: number
  name: string
  saving: boolean
  error: string | null
  options: EditOption[]


  newOptions: DraftOption[]
  newOptionErrors: Record<number, string>
  savingNewOptions: boolean
}

const editVariations = ref<EditVariation[]>([])

watchEffect(() => {
  if (mode.value !== 'update' || !props.categoryId) return

  editVariations.value = existingVariations.value.map((v) => ({
    id: v.id,
    name: v.name,
    saving: false,
    error: null,
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

async function updateVariationName(v: EditVariation) {
  v.saving = true
  v.error = null
  try {
    await variationStore.update(v.id, { name: v.name.trim() })
  } catch {
    v.error = variationStore.error ?? 'Failed to update variation'
  } finally {
    v.saving = false
  }
}

async function updateOptionValue(o: EditOption) {
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

function addNewOptionToExisting(v: EditVariation) {
  v.newOptions.push({ value: '' })
}

function removeNewOptionFromExisting(v: EditVariation, i: number) {
  v.newOptions.splice(i, 1)
  const next: Record<number, string> = {}
  v.newOptions.forEach((_, idx) => {
    if (v.newOptionErrors[idx]) next[idx] = v.newOptionErrors[idx]
  })
  v.newOptionErrors = next
}

function validateNewOptions(v: EditVariation) {
  const errs: Record<number, string> = {}

  v.newOptions.forEach((o, i) => {
    const val = o.value.trim()
    if (!val) errs[i] = 'Please enter a value'
    else if (val.length < 2) errs[i] = 'Must be at least 2 characters'
  })

  const seen = new Map<string, number>()
  v.newOptions.forEach((o, i) => {
    const key = o.value.trim().toLowerCase()
    if (!key) return
    if (seen.has(key)) {
      errs[i] = 'Duplicate value'
      errs[seen.get(key)!] = 'Duplicate value'
    } else {
      seen.set(key, i)
    }
  })

  v.newOptionErrors = errs
  return Object.keys(errs).length === 0
}

async function saveNewOptions(v: EditVariation) {
  v.error = null
  if (!validateNewOptions(v)) return

  const values = v.newOptions.map((o) => o.value.trim()).filter(Boolean)
  if (values.length === 0) return

  v.savingNewOptions = true
  try {
    for (const value of values) {
      const created = await variationOptionStore.create({ variation_id: v.id, value })
      if (!created?.id) {
        v.error = variationOptionStore.error ?? 'Failed to add option'
        return
      }
      // show immediately
      v.options.push({ id: created.id, value: created.value, saving: false, error: null })
    }

    v.newOptions = [{ value: '' }]
    v.newOptionErrors = {}
  } finally {
    v.savingNewOptions = false
  }
}

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

      <!-- UPDATE -->
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

            <button
              class="btn btn-primary btn-sm"
              @click="updateVariationName(v)"
              :disabled="v.saving"
            >
              <span v-if="v.saving" class="loading loading-spinner loading-xs"></span>
              Update
            </button>
          </div>

          <div v-if="v.error" class="text-sm text-error">{{ v.error }}</div>

          <div class="space-y-2">
            <div class="font-medium">Options</div>

            <div v-for="o in v.options" :key="o.id" class="flex gap-2 items-center">
              <input v-model="o.value" class="input input-bordered flex-1" />
              <button
                class="btn btn-secondary btn-sm"
                @click="updateOptionValue(o)"
                :disabled="o.saving"
              >
                <span v-if="o.saving" class="loading loading-spinner loading-xs"></span>
                Update
              </button>
            </div>

            <div v-if="v.options.length === 0" class="text-sm opacity-70">No options yet.</div>
          </div>

          <!-- Add NEW options -->
          <div class="mt-3 space-y-2">
            <div class="flex items-center justify-between">
              <div class="font-medium">Add new options</div>
              <button
                type="button"
                class="btn btn-outline btn-xs btn-square"
                @click="addNewOptionToExisting(v)"
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
                @click="removeNewOptionFromExisting(v, ni)"
                :disabled="v.savingNewOptions"
                title="Remove option"
              >
                ✕
              </button>
            </div>

            <button
              type="button"
              class="btn btn-secondary btn-sm"
              @click="saveNewOptions(v)"
              :disabled="v.savingNewOptions"
            >
              <span v-if="v.savingNewOptions" class="loading loading-spinner loading-xs"></span>
              Add options
            </button>
          </div>
        </div>
      </div>

      <!-- Add NEW variations  -->
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
                :disabled="v.savingVariation || v.savingOptions"
              />
            </div>

            <button
              type="button"
              class="btn btn-primary btn-sm"
              @click="saveDraftVariation(v)"
              :disabled="!categoryId || v.savingVariation || v.savingOptions"
            >
              <span v-if="v.savingVariation" class="loading loading-spinner loading-xs"></span>
              {{ v.id ? 'Saved' : 'Save' }}
            </button>

            <button
              type="button"
              class="btn btn-ghost btn-sm btn-square"
              @click="removeDraftVariation(vi)"
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
                @click="addDraftOption(v)"
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
                @click="removeDraftOption(v, oi)"
                :disabled="!v.id || v.savingOptions || v.savingVariation"
                title="Remove option"
              >
                ✕
              </button>
            </div>

            <button
              type="button"
              class="btn btn-secondary btn-sm"
              @click="saveDraftOptions(v)"
              :disabled="!v.id || v.savingOptions || v.savingVariation"
            >
              <span v-if="v.savingOptions" class="loading loading-spinner loading-xs"></span>
              Save options
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
