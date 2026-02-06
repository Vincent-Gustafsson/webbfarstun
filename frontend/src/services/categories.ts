import { http } from '../utils/http'
import type { Category, CategoryCreate, CategoryUpdate } from '../types/category'

export default {
  async getAll() {
    return http.get<Category[]>('/categories/')
  },

  async getOne(id: number) {
    return http.get<Category>(`/categories/${id}`)
  },

  async create(data: CategoryCreate) {
    return http.post<Category>('/categories/', data)
  },

  async update(id: number, data: CategoryUpdate) {
    return http.patch<Category>(`/categories/${id}`, data)
  },

  async delete(id: number) {
    return http.delete<void>(`/categories/${id}`)
  },
}
