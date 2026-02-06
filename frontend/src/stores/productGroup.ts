import { defineStore } from 'pinia'
import productGroupService from '@/services/productGroups'
import type { ProductGroup, ProductGroupCreate } from '@/types/productGroup'
import { getErrorMessage } from '@/utils/error'

export const useProductGroupStore = defineStore('productGroup', {
  state: () => ({
    productGroups: [] as ProductGroup[],
    loading: false,
    error: null as string | null,
  }),

  actions: {
    async fetchAll() {
      this.loading = true
      try {
        this.productGroups = await productGroupService.getAll()
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
      } finally {
        this.loading = false
      }
    },

    async create(payload: ProductGroupCreate) {
      this.loading = true
      this.error = null
      try {
        const newGroup = await productGroupService.create(payload)
        this.productGroups.push(newGroup)
        return newGroup // Return so the UI can close the modal
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        throw err
      } finally {
        this.loading = false
      }
    },

    async remove(id: number) {
      const previous = [...this.productGroups]
      this.productGroups = this.productGroups.filter((pg) => pg.id !== id)

      try {
        await productGroupService.delete(id)
      } catch (err: unknown) {
        this.productGroups = previous
        this.error = getErrorMessage(err)
      }
    },
  },
})
