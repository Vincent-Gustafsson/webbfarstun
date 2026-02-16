import { defineStore } from 'pinia'
import { getErrorMessage } from '@/utils/error'
import adminProductGroupService from '@/services/admin/adminCreateProductGroup'
import type {
  ProductGroup,
  ProductGroupCreate,
  ProductGroupUpdate,
} from '@/types/admin/adminCreateProductGroup'

export const useProductGroupStore = defineStore('productGroup', {
  state: () => ({
    productGroups: [] as ProductGroup[],
    loading: false,
    error: null as string | null,
    fieldErrors: {} as Partial<Record<keyof ProductGroupCreate, string>>,
    lastFetched: null as number | null,
    createdId: null as number | null,
  }),

  getters: {},

  actions: {
    async fetchAll(force = false) {
      const now = Date.now()
      if (
        !force &&
        this.productGroups.length > 0 &&
        this.lastFetched &&
        now - this.lastFetched < 5 * 60 * 1000
      ) {
        return
      }

      this.loading = true
      this.error = null

      try {
        this.productGroups = await adminProductGroupService.getAll()
        this.lastFetched = now
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async create(payload: ProductGroupCreate) {
      this.loading = true
      this.error = null
      this.fieldErrors = {}

      try {
        const newProductGroup = await adminProductGroupService.create(payload)
        this.productGroups.push(newProductGroup)
        this.createdId = newProductGroup.id
      } catch (err: any) {
        const data = err?.data
        const errors = data?.detail?.errors

        if (errors && typeof errors === 'object') {
          this.fieldErrors = errors
          this.error = null
        } else {
          this.error = err?.message ?? 'Failed to create product group'
          this.fieldErrors = {}
        }
      } finally {
        this.loading = false
      }
    },

    async update(id: number, payload: ProductGroupUpdate) {
      this.loading = true
      try {
        const updatedProductGroup = await adminProductGroupService.update(id, payload)

        const index = this.productGroups.findIndex((pg) => pg.id === id)
        if (index !== -1) {
          this.productGroups[index] = updatedProductGroup
        }
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async remove(id: number) {
      const previousProduct = [...this.productGroups]

      this.productGroups = this.productGroups.filter((pg) => pg.id !== id)

      try {
        await adminProductGroupService.delete(id)
      } catch (err: unknown) {
        this.productGroups = previousProduct
        this.error = 'Failed to delete product group'
        alert('Could not delete product group.')
      }
    },
  },
})
