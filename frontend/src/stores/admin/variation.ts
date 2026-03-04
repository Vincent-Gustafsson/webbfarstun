import { defineStore } from 'pinia'
import adminVariationService from '@/services/admin/variation'
import type { Variation, VariationCreate, VariationUpdate } from '@/types/admin/variation'
import { getErrorMessage } from '@/utils/error'

export const useVariationStore = defineStore('variation', {
  state: () => ({
    variations: [] as Variation[],
    loading: false,
    error: null as string | null,
    fieldErrors: {} as Partial<Record<keyof VariationCreate, string>>,
    lastFetched: null as number | null,
  }),

  getters: {},

  actions: {
    async fetchAll(force = false) {
      const now = Date.now()
      if (
        !force &&
        this.variations.length > 0 &&
        this.lastFetched &&
        now - this.lastFetched < 5 * 60 * 1000
      ) {
        return
      }

      this.loading = true
      this.error = null

      try {
        this.variations = await adminVariationService.getAll()
        this.lastFetched = now
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async create(payload: VariationCreate) {
      this.loading = true
      this.error = null
      this.fieldErrors = {}

      try {
        const newVariation = await adminVariationService.create(payload)
        this.variations.push(newVariation)
        return newVariation
      } catch (err: any) {
        const data = err?.data
        const errors = data?.detail?.errors

        if (errors && typeof errors === 'object') {
          this.fieldErrors = errors
          this.error = null
        } else {
          this.error = err?.message ?? 'Failed to create variation'
          this.fieldErrors = {}
        }
      } finally {
        this.loading = false
      }
    },

    async update(id: number, payload: VariationUpdate) {
      this.loading = true
      try {
        const updatedVariation = await adminVariationService.update(id, payload)

        const index = this.variations.findIndex((c) => c.id === id)
        if (index !== -1) {
          this.variations[index] = updatedVariation
        }
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async remove(id: number) {
      const previousProduct = [...this.variations]

      this.variations = this.variations.filter((c) => c.id !== id)

      try {
        await adminVariationService.delete(id)
      } catch (err: unknown) {
        this.variations = previousProduct
        this.error = 'Failed to delete item'
        alert('Could not delete Variation.')
      }
    },
  },
})
