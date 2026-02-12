import { defineStore } from 'pinia'
import categoryService from '../services/categories'
import { buildCategoryTree } from '../utils/tree'
import type { Category, CategoryCreate, CategoryUpdate, CategoryNode } from '../types/category'
import { getErrorMessage } from '@/utils/error'

export const useCategoryStore = defineStore('category', {
  state: () => ({
    categories: [] as Category[],
    loading: false,
    error: null as string | null,
    lastFetched: null as number | null,
  }),

  getters: {
    tree: (state): CategoryNode[] => buildCategoryTree(state.categories),

    // Usage: store.getById(123)
    getById: (state) => (id: number) => state.categories.find((c) => c.id === id) ?? null,
  },

  actions: {
    upsert(category: Category) {
      const index = this.categories.findIndex((c) => c.id === category.id)
      if (index === -1) this.categories.push(category)
      else this.categories[index] = category
    },

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
        this.categories = await categoryService.getAll()
        this.lastFetched = now
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    // Usage: await store.fetchOne(123)
    async fetchOne(id: number, opts?: { force?: boolean }) {
      const force = opts?.force ?? false

      // If you already have it and not forcing, just return it
      const existing = this.categories.find((c) => c.id === id)
      if (existing && !force) return existing

      this.loading = true
      this.error = null
      try {
        const category = await categoryService.getOne(id)
        this.upsert(category)
        return category
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
        return null
      } finally {
        this.loading = false
      }
    },

    async create(payload: CategoryCreate) {
      this.loading = true
      this.error = null
      try {
        const newCategory = await categoryService.create(payload)
        this.categories.push(newCategory)
        return newCategory
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
        return null
      } finally {
        this.loading = false
      }
    },

    async update(id: number, payload: CategoryUpdate) {
      this.loading = true
      this.error = null
      try {
        const updatedCategory = await categoryService.update(id, payload)
        this.upsert(updatedCategory)
        return updatedCategory
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
        return null
      } finally {
        this.loading = false
      }
    },

    async remove(id: number) {
      const previousCategories = [...this.categories]
      this.categories = this.categories.filter((c) => c.id !== id)

      try {
        await categoryService.delete(id)
      } catch (err: unknown) {
        this.categories = previousCategories
        this.error = getErrorMessage(err) || 'Failed to delete item'
        alert('Could not delete category.')
      }
    },
  },
})
