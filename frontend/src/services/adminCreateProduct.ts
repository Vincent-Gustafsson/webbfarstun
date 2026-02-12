import { http } from '../utils/http'
import type { Product, ProductCreate, ProductUpdate } from '../types/adminCreateProduct'

export default {
  async getAll() {
    return http.get<Product[]>('/products/')
  },

  async getOne(id: number) {
    return http.get<Product>(`/products/${id}`)
  },

  async create(data: ProductCreate) {
    return http.post<Product>('/products/', data)
  },

  async update(id: number, data: ProductUpdate) {
    return http.patch<Product>(`/products/${id}`, data)
  },

  async delete(id: number) {
    return http.delete<void>(`/products/${id}`)
  },
}
