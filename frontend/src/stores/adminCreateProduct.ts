import { defineStore } from 'pinia'
import productService from '../services/adminCreateProduct'
import type { Product, ProductCreate, ProductUpdate } from '../types/adminCreateProduct'
import { getErrorMessage } from '@/utils/error'

export const useProductStore = defineStore('product', {
  state: () => ({
    products: [] as Product[],
    loading: false,
    error: null as string | null,
    fieldErrors: {} as Partial<Record<keyof ProductCreate, string>>,
    lastFetched: null as number | null,
  }),

  getters: {
    productCount: (state) => state.products.length,
  },

  actions: {
    async fetchAll(force = false) {
      const now = Date.now()
      if (
        !force &&
        this.products.length > 0 &&
        this.lastFetched &&
        now - this.lastFetched < 5 * 60 * 1000
      ) {
        return
      }

      this.loading = true
      this.error = null

      try {
        this.products = await productService.getAll()
        this.lastFetched = now
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async create(payload: ProductCreate) {
      this.loading = true
      this.error = null
      this.fieldErrors = {}

      try {
        const newProduct = await productService.create(payload)
        this.products.push(newProduct)
        return newProduct
      } catch (err: any) {
        const data = err?.data
        const errors = data?.detail?.errors

        if (errors && typeof errors === 'object') {
          this.fieldErrors = errors
          this.error = null
        } else {
          this.error = err?.message ?? 'Failed to create product'
          this.fieldErrors = {}
        }
      } finally {
        this.loading = false
      }
    },

    async update(id: number, payload: ProductUpdate) {
      this.loading = true
      try {
        const updatedProduct = await productService.update(id, payload)

        const index = this.products.findIndex((c) => c.id === id)
        if (index !== -1) {
          this.products[index] = updatedProduct
        }
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    async remove(id: number) {
      const previousProduct = [...this.products]

      this.products = this.products.filter((c) => c.id !== id)

      try {
        await productService.delete(id)
      } catch (err: unknown) {
        this.products = previousProduct
        this.error = 'Failed to delete item'
        alert('Could not delete Product.')
      }
    },
  },
})
