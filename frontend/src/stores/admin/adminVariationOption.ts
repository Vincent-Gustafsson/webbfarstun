import { defineStore } from 'pinia'
import adminVariationOptionService from '@/services/admin/adminVariationOption'
import type {
  VariationOption,
  VariationOptionCreate,
  VariationOptionUpdate,
} from '@/types/admin/adminVariationOption'
import { getErrorMessage } from '@/utils/error'

export const useVariationOptionStore = defineStore('variationOption', {
  state: () => ({
    variationOptions: [] as VariationOption[],
    loading: false,
    error: null as string | null,
    fieldErrors: {} as Partial<Record<keyof VariationOptionCreate, string>>,
    lastFetched: null as number | null,
  }),

  getters: {},

  actions: {
    async fetchAll(force = false) {
      const now = Date.now()
      if (
        !force &&
        this.variationOptions.length > 0 &&
        this.lastFetched &&
        now - this.lastFetched < 5 * 60 * 1000
      ) {
        return
      }

      this.loading = true
      this.error = null

      try {
        this.variationOptions = await adminVariationOptionService.getAll()
        this.lastFetched = now
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async create(payload: VariationOptionCreate) {
      this.loading = true
      this.error = null
      this.fieldErrors = {}

      try {
        const newVariationOption = await adminVariationOptionService.create(payload)
        this.variationOptions.push(newVariationOption)
        return newVariationOption
      } catch (err: any) {
        const data = err?.data
        const errors = data?.detail?.errors

        if (errors && typeof errors === 'object') {
          this.fieldErrors = errors
          this.error = null
        } else {
          this.error = err?.message ?? 'Failed to create variation option'
          this.fieldErrors = {}
        }
      } finally {
        this.loading = false
      }
    },

    async update(id: number, payload: VariationOptionUpdate) {
      this.loading = true
      try {
        const updatedVariationOption = await adminVariationOptionService.update(id, payload)

        const index = this.variationOptions.findIndex((c) => c.id === id)
        if (index !== -1) {
          this.variationOptions[index] = updatedVariationOption
        }
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async remove(id: number) {
      const previousProduct = [...this.variationOptions]

      this.variationOptions = this.variationOptions.filter((c) => c.id !== id)

      try {
        await adminVariationOptionService.delete(id)
      } catch (err: unknown) {
        this.variationOptions = previousProduct
        this.error = 'Failed to delete Variation option'
        alert('Could not delete Variation option.')
      }
    },
  },
})
