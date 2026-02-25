<script setup lang="ts">
import { computed, ref, watch, onBeforeUnmount, onMounted } from 'vue'
import { useProductImageStore } from '@/stores/admin/adminImage'
import { useProductStore } from '@/stores/admin/adminCreateProduct'

const props = defineProps<{
  productId: number
  disabled?: boolean
}>()

const imageStore = useProductImageStore()
const productStore = useProductStore()

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

function onPick(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files ? Array.from(input.files) : []
  localError.value = null

  clearAllPreviews()
  picked.value = files.map((f) => ({
    file: f,
    previewUrl: URL.createObjectURL(f),
    status: 'queued',
  }))

  input.value = ''
}

function removePicked(i: number) {
  const p = picked.value[i]
  if (p) URL.revokeObjectURL(p.previewUrl)
  picked.value.splice(i, 1)

  if (picked.value.length === 0) {
    defaultIndex.value = 0
    return
  }
  if (defaultIndex.value === i) {
    defaultIndex.value = 0
  } else if (defaultIndex.value > i) {
    defaultIndex.value -= 1
  }
}

async function uploadAll() {
  localError.value = null
  if (!props.productId) return (localError.value = 'Create the product first.')
  if (picked.value.length === 0) return (localError.value = 'Pick at least one file.')

  let newDefaultImageId: number | null = null

  for (let i = 0; i < picked.value.length; i++) {
    const p = picked.value[i]
    if (p.status === 'done') continue

    p.status = 'uploading'
    p.error = undefined

    try {
      const created = await imageStore.upload(props.productId, p.file, { is_default: false })

      if (!created?.id) {
        p.status = 'error'
        p.error = imageStore.error ?? 'Upload failed'
      } else {
        p.status = 'done'
        if (i === defaultIndex.value) newDefaultImageId = created.id
      }
    } catch (err: any) {
      p.status = 'error'
      p.error = err?.message ?? imageStore.error ?? 'Upload failed'
    }
  }

  if (newDefaultImageId) {
    await imageStore.setDefault(props.productId, newDefaultImageId)
  }

  await refresh()
  picked.value = []
  defaultIndex.value = 0
}

const existing = computed(() =>
  (imageStore.images ?? []).filter((img: any) => {
    const pid = Number(img.product_id ?? img.productId)
    return pid === Number(props.productId)
  }),
)

async function refresh() {
  if (!props.productId) return
  await imageStore.fetchAll()
}
onMounted(refresh)

async function makeDefault(imageId: number) {
  const updated = await imageStore.setDefault(props.productId, imageId)

  if (productStore.current?.id === props.productId) productStore.current.default_image = updated
  const listItem = productStore.products.find((p) => p.id === props.productId)
  if (listItem) listItem.default_image = updated
}

async function deleteExisting(imageId: number) {
  await imageStore.remove(imageId)
  await refresh()
}

watch(
  () => props.productId,
  async () => {
    clearAllPreviews()
    picked.value = []
    localError.value = null

    await refresh()
  },
)

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) || window.location.origin

function imgSrc(img: any) {
  const id = Number(img?.id)
  if (Number.isFinite(id) && id > 0) {
    return `${API_BASE.replace(/\/$/, '')}/api/product-images/${id}/file`
  }

  return ''
}

const defaultIndex = ref<number>(0)
</script>

<template>
  <section class="card bg-base-100 shadow-xl max-w-3xl">
    <div class="card-body space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="card-title text-xl">Images</h3>
        <div class="text-sm opacity-70">Product #{{ productId }}</div>
      </div>
      <div v-if="existing.length" class="space-y-2">
        <div class="font-medium">Current images</div>

        <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
          <div v-for="img in existing" :key="img.id" class="rounded-box border border-base-300 p-2">
            <div class="aspect-square rounded-box overflow-hidden border border-base-300">
              <img v-if="imgSrc(img)" :src="imgSrc(img)" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full bg-base-200"></div>
            </div>

            <div class="flex items-center justify-between pt-2 gap-2">
              <button
                class="btn btn-xs btn-primary"
                :disabled="disabled || isBusy || img.is_default"
                @click="makeDefault(img.id)"
              >
                {{ img.is_default ? 'Default' : 'Make default' }}
              </button>

              <button
                class="btn btn-xs btn-error btn-soft"
                :disabled="disabled || isBusy"
                @click="deleteExisting(img.id)"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
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
                  class="btn btn-soft btn-error btn-xs"
                  :disabled="disabled || isBusy"
                  @click="removePicked(i)"
                >
                  Remove
                </button>
              </div>
              <div class="flex items-center gap-2">
                <label class="flex items-center gap-2 text-sm cursor-pointer select-none">
                  <input
                    type="radio"
                    class="radio radio-primary radio-sm"
                    name="main-image"
                    :disabled="disabled || isBusy"
                    :checked="defaultIndex === i"
                    @change="defaultIndex = i"
                  />
                </label>

                <span v-if="defaultIndex === i" class="badge badge-primary badge-sm">Default</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-sm opacity-70">Pick one or more images to upload.</div>
    </div>
  </section>
</template>
