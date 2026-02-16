// src/stores/products.ts
import { defineStore } from 'pinia'
import productService from '@/services/products'
import type { ProductCreate, ProductListItem, ProductPublic, ProductUpdate } from '@/types/product'
import { getErrorMessage } from '@/utils/error'

export const useProductStore = defineStore('product', {
  state: () => ({
    products: [] as ProductListItem[],
    activeProduct: null as ProductPublic | null,
    loading: false,
    error: null as string | null,
  }),

  getters: {
    getById: (state) => (id: number) => state.products.find((p) => p.id === id) ?? null,
  },

  actions: {
    clearError() {
      this.error = null
    },

    setActiveProduct(product: ProductPublic | null) {
      this.activeProduct = product
    },

    upsertListItem(item: ProductListItem) {
      const i = this.products.findIndex((p) => p.id === item.id)
      if (i === -1) this.products.push(item)
      else this.products[i] = item
    },

    async fetchAll(params?: Record<string, any>) {
      this.loading = true
      this.error = null
      try {
        this.products = await productService.getAll(params ?? {})
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    // No caching: always hits the API and sets activeProduct
    async fetchOne(id: number) {
      this.loading = true
      this.error = null
      try {
        const product = (await productService.getOne(id)) as ProductPublic
        this.activeProduct = product

        // optional: also keep list roughly in sync (map details -> list shape)
        this.upsertListItem({
          id: product.id,
          name: product.name,
          price: product.price,
          stock_qty: product.stock_qty,
          sku: product.sku ?? null,
          product_group_id: product.product_group_id,
          category_id: (product as any).category_id ?? null,
          options: product.options ?? [],
        })

        return product
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
        this.activeProduct = null
        return null
      } finally {
        this.loading = false
      }
    },

    async create(payload: ProductCreate) {
      this.loading = true
      this.error = null
      try {
        const created = (await productService.create(payload)) as ProductPublic

        this.upsertListItem({
          id: created.id,
          name: created.name,
          price: created.price,
          stock_qty: created.stock_qty,
          sku: created.sku ?? null,
          product_group_id: created.product_group_id,
          category_id: (payload as any).category_id ?? null,
          options: created.options ?? [],
        })

        return created
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
        return null
      } finally {
        this.loading = false
      }
    },

    async update(id: number, payload: ProductUpdate) {
      this.loading = true
      this.error = null
      try {
        const updated = await productService.update(id, payload)

        // best-effort merge into list
        const existing = this.products.find((p) => p.id === id)
        if (existing) this.upsertListItem({ ...existing, ...updated, id } as ProductListItem)

        // optional: keep activeProduct in sync if it’s the same one
        if (this.activeProduct?.id === id) {
          this.activeProduct = { ...this.activeProduct, ...(updated as any) }
        }

        return updated
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
        return null
      } finally {
        this.loading = false
      }
    },

    async remove(id: number) {
      const previous = [...this.products]
      this.products = this.products.filter((p) => p.id !== id)

      try {
        await productService.delete(id)
        if (this.activeProduct?.id === id) this.activeProduct = null
      } catch (err: unknown) {
        this.products = previous
        this.error = getErrorMessage(err) || 'Failed to delete item'
        alert('Could not delete product.')
      }
    },
  },
})
