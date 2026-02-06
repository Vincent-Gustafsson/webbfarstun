import { defineStore } from 'pinia'
import categoryService from '../services/categories'
import { buildCategoryTree } from '../utils/tree'
import type { Category, CategoryCreate, CategoryUpdate, CategoryNode } from '../types/category'
import { getErrorMessage } from '@/utils/error'

export const useCategoryStore = defineStore('category', {
  // 1. STATE: The data you want to track
  state: () => ({
    categories: [] as Category[],
    loading: false,
    error: null as string | null,
    lastFetched: null as number | null, // To manage caching invalidation
  }),

  // 2. GETTERS: Computed values (like Python properties)
  getters: {
    tree: (state): CategoryNode[] => buildCategoryTree(state.categories),
  },

  // 3. ACTIONS: Methods that modify state or call APIs
  actions: {
    async fetchAll(force = false) {
      // Basic Cache check: If we fetched less than 5 mins ago, don't re-fetch
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
        // Use the service we built earlier
        this.categories = await categoryService.getAll()
        this.lastFetched = now
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async create(payload: CategoryCreate) {
      this.loading = true
      try {
        const newCategory = await categoryService.create(payload)
        // MUTATION: Add to the list immediately (no need to re-fetch whole list)
        this.categories.push(newCategory)
        return newCategory
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async update(id: number, payload: CategoryUpdate) {
      this.loading = true
      try {
        const updatedCategory = await categoryService.update(id, payload)
        // MUTATION: Find the item in the array and update it
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
      // Optimistic Update Pattern:
      // 1. Snapshot the current list
      const previousCategories = [...this.categories]

      // 2. Update UI immediately (feels instant to user)
      this.categories = this.categories.filter((c) => c.id !== id)

      try {
        // 3. Perform actual network request
        await categoryService.delete(id)
      } catch (err: unknown) {
        // 4. If it fails, roll back the state
        this.categories = previousCategories
        this.error = 'Failed to delete item'
        alert('Could not delete category.') // or use a toast
      }
    },
  },
})
