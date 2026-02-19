<script setup lang="ts">
import { computed, ref, watch, onBeforeUnmount } from 'vue'
import { useProductImageStore } from '@/stores/admin/adminImage'

const props = defineProps<{
  productId: number
  disabled?: boolean
}>()

const imageStore = useProductImageStore()

type PickedFile = {
  file: File
  previewUrl: string
  status: 'queued' | 'uploading' | 'done' | 'error'
  error?: string
}

const picked = ref<PickedFile[]>([])
const localError = ref<string | null>(null)

const isBusy = computed(
  () => imageStore.loading || picked.value.some((p) => p.status === 'uploading'),
)
const canUpload = computed(
  () => !!props.productId && picked.value.length > 0 && !props.disabled && !isBusy.value,
)

function clearAllPreviews() {
  for (const p of picked.value) URL.revokeObjectURL(p.previewUrl)
}

onBeforeUnmount(() => {
  clearAllPreviews()
})

watch(
  () => props.productId,
  () => {
    clearAllPreviews()
    picked.value = []
    localError.value = null
  },
)

function onPick(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files ? Array.from(input.files) : []
  localError.value = null

  // clear previous selection
  clearAllPreviews()
  picked.value = files.map((f) => ({
    file: f,
    previewUrl: URL.createObjectURL(f),
    status: 'queued',
  }))

  // allow re-picking same file
  input.value = ''
}

function removePicked(i: number) {
  const p = picked.value[i]
  if (p) URL.revokeObjectURL(p.previewUrl)
  picked.value.splice(i, 1)
}

async function uploadAll() {
  localError.value = null
  if (!props.productId) {
    localError.value = 'Create the product first.'
    return
  }
  if (picked.value.length === 0) {
    localError.value = 'Pick at least one file.'
    return
  }

  for (const p of picked.value) {
    if (p.status === 'done') continue

    p.status = 'uploading'
    p.error = undefined
    try {
      const created = await imageStore.upload(props.productId, p.file)
      if (!created?.id) {
        p.status = 'error'
        p.error = imageStore.error ?? 'Upload failed'
      } else {
        p.status = 'done'
      }
    } catch (err: any) {
      p.status = 'error'
      p.error = err?.message ?? imageStore.error ?? 'Upload failed'
    }
  }
}

async function uploadOne(i: number) {
  localError.value = null
  const p = picked.value[i]
  if (!p) return
  if (!props.productId) return (localError.value = 'Create the product first.')

  p.status = 'uploading'
  p.error = undefined
  try {
    const created = await imageStore.upload(props.productId, p.file)
    if (!created?.id) {
      p.status = 'error'
      p.error = imageStore.error ?? 'Upload failed'
    } else {
      p.status = 'done'
    }
  } catch (err: any) {
    p.status = 'error'
    p.error = err?.message ?? imageStore.error ?? 'Upload failed'
  }
}
</script>

<template>
  <section class="card bg-base-100 shadow-xl max-w-3xl">
    <div class="card-body space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="card-title text-xl">Images</h3>
        <div class="text-sm opacity-70">Product #{{ productId }}</div>
      </div>

      <input
        type="file"
        class="file-input file-input-bordered w-full"
        multiple
        accept="image/*"
        :disabled="disabled || isBusy"
        @change="onPick"
      />

      <div v-if="localError" class="alert alert-error">
        <span>{{ localError }}</span>
      </div>

      <div v-if="imageStore.error" class="alert alert-error">
        <span>{{ imageStore.error }}</span>
      </div>

      <div v-if="picked.length" class="space-y-3">
        <div class="flex items-center justify-between">
          <div class="font-medium">Selected files ({{ picked.length }})</div>

          <button class="btn btn-primary btn-sm" :disabled="!canUpload" @click="uploadAll">
            <span v-if="isBusy" class="loading loading-spinner loading-xs"></span>
            Upload all
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div
            v-for="(p, i) in picked"
            :key="p.file.name + i"
            class="rounded-box border border-base-300 p-3 flex gap-3"
          >
            <div class="w-20 h-20 rounded-box overflow-hidden border border-base-300 shrink-0">
              <img :src="p.previewUrl" class="w-full h-full object-cover" alt="" />
            </div>

            <div class="flex-1 min-w-0 space-y-1">
              <div class="font-medium truncate">{{ p.file.name }}</div>
              <div class="text-xs opacity-70">{{ Math.round(p.file.size / 1024) }} KB</div>

              <div v-if="p.status === 'error'" class="text-sm text-error">
                {{ p.error ?? 'Upload failed' }}
              </div>
              <div v-else-if="p.status === 'done'" class="text-sm text-success">Uploaded</div>
              <div v-else-if="p.status === 'uploading'" class="text-sm opacity-80">Uploading…</div>
              <div v-else class="text-sm opacity-80">Queued</div>

              <div class="flex gap-2 pt-1">
                <button
                  class="btn btn-secondary btn-xs"
                  :disabled="disabled || isBusy || p.status === 'done'"
                  @click="uploadOne(i)"
                >
                  Upload
                </button>

                <button
                  class="btn btn-ghost btn-xs"
                  :disabled="disabled || isBusy"
                  @click="removePicked(i)"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-sm opacity-70">Pick one or more images to upload.</div>
    </div>
  </section>
</template>
