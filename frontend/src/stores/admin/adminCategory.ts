import { defineStore } from 'pinia'
import adminCategoryService from '@/services/admin/adminCategory'
import type { Variation, VariationCreate, VariationUpdate } from '@/types/admin/adminVariation'
import { getErrorMessage } from '@/utils/error'
import type { CategoryUpdate, CategoryCreate } from '@/types/admin/adminCategory'

export const useCategoryStore = defineStore('category', {
  state: () => ({
    categories: [] as Category[],
    loading: false,
    error: null as string | null,
    fieldErrors: {} as Partial<Record<keyof CategoryCreate, string>>,
    lastFetched: null as number | null,
    createdId: null as number | null,
    currentCategory: null as Category | null,
  }),

  getters: {},

  actions: {
    async fetchAll(force = false) {
      const now = Date.now()
      if (
        !force &&
        this.categories.length > 0 &&
        this.lastFetched &&
        now - this.lastFetched < 5 * 60 * 1000
      ) {
        return
      }

      this.loading = true
      this.error = null

      try {
        this.categories = await adminCategoryService.getAll()
        this.lastFetched = now
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async fetchById(id: number) {
      this.loading = true
      this.error = null

      try {
        const category = await adminCategoryService.getOne(id)
        this.currentCategory = category

        const i = this.categories.findIndex((c) => c.id === id)
        if (i !== -1) this.categories[i] = category
        else this.categories.push(category)

        return category
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async create(payload: CategoryCreate) {
      this.loading = true
      this.error = null
      this.fieldErrors = {}

      try {
        const newCategory = await adminCategoryService.create(payload)
        this.categories.push(newCategory)
        this.createdId = newCategory.id
      } catch (err: any) {
        const data = err?.data
        const errors = data?.detail?.errors

        if (errors && typeof errors === 'object') {
          this.fieldErrors = errors
          this.error = null
        } else {
          this.error = err?.message ?? 'Failed to create category'
          this.fieldErrors = {}
        }
      } finally {
        this.loading = false
      }
    },

    async update(id: number, payload: CategoryUpdate) {
      this.loading = true
      try {
        const updatedCategory = await adminCategoryService.update(id, payload)

        const index = this.categories.findIndex((c) => c.id === id)
        if (index !== -1) {
          this.categories[index] = updatedCategory
        }
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async remove(id: number) {
      const previousProduct = [...this.categories]

      this.categories = this.categories.filter((c) => c.id !== id)

      try {
        await adminCategoryService.delete(id)
      } catch (err: unknown) {
        this.categories = previousProduct
        this.error = 'Failed to delete category'
        alert('Could not delete category.')
      }
    },
  },
})
