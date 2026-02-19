import { defineStore } from 'pinia'
import adminImageService from '@/services/admin/adminImage'
import type { ProductImage, ProductImageCreate, ProductImageUpdate } from '@/types/admin/adminImage'
import { getErrorMessage } from '@/utils/error'

export const useProductImageStore = defineStore('productImage', {
  state: () => ({
    images: [] as ProductImage[],
    loading: false,
    error: null as string | null,
    fieldErrors: {} as Partial<Record<keyof ProductImageCreate, string>>,
  }),

  actions: {
    async fetchAll() {
      this.loading = true
      this.error = null
      try {
        this.images = await adminImageService.getAll()
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async create(payload: ProductImageCreate) {
      this.loading = true
      this.error = null
      this.fieldErrors = {}
      try {
        const created = await adminImageService.create(payload)
        this.images.push(created)
        return created
      } catch (err: any) {
        const data = err?.data
        const errors = data?.detail?.errors
        if (errors && typeof errors === 'object') {
          this.fieldErrors = errors
          this.error = null
        } else {
          this.error = err?.message ?? 'Failed to create image'
        }
      } finally {
        this.loading = false
      }
    },

    async update(id: number, payload: ProductImageUpdate) {
      this.loading = true
      this.error = null
      try {
        const updated = await adminImageService.update(id, payload)
        const i = this.images.findIndex((x) => x.id === id)
        if (i !== -1) this.images[i] = updated
        return updated
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async remove(id: number) {
      const prev = [...this.images]
      this.images = this.images.filter((x) => x.id !== id)
      try {
        await adminImageService.delete(id)
      } catch (err: unknown) {
        this.images = prev
        this.error = 'Failed to delete image'
        alert('Could not delete image.')
      }
    },

    async upload(productId: number, file: File) {
      this.loading = true
      this.error = null
      this.fieldErrors = {}

      try {
        const created = await adminImageService.uploadProductImage(productId, file)
        this.images.push(created)
        return created
      } catch (err: any) {
        const data = err?.data
        const errors = data?.detail?.errors
        if (errors && typeof errors === 'object') {
          this.fieldErrors = errors
          this.error = null
        } else {
          this.error = err?.message ?? 'Failed to upload image'
        }
      } finally {
        this.loading = false
      }
    },
  },
})
