import { defineStore } from 'pinia'
import productService from '../services/adminCreateProduct'
import type { Product, ProductCreate, ProductUpdate } from '../types/adminCreateProduct'
import { getErrorMessage } from '@/utils/error'

export const useProductStore = defineStore('product', {
  state: () => ({
    products: [] as Product[],
    loading: false,
    error: null as string | null,
    lastFetched: null as number | null,
  }),

  getters: {
    productCount: (state) => state.products.length,

    productBySku: (state) => {
      return (sku: string) => state.products.find((p) => (p as any).sku === sku)
    },
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
      try {
        const newProduct = await productService.create(payload)
        this.products.push(newProduct)
        return newProduct
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
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
