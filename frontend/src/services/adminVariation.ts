import { http } from '../utils/http'
import type { Variation, VariationCreate, VariationUpdate } from '../types/adminVariation'

export default {
  async getAll() {
    return http.get<Variation[]>('/variations/')
  },

  async getOne(id: number) {
    return http.get<Variation>(`/variations/${id}`)
  },

  async create(data: VariationCreate) {
    return http.post<Variation>('/variations/', data)
  },

  async update(id: number, data: VariationUpdate) {
    return http.patch<Variation>(`/variations/${id}`, data)
  },

  async delete(id: number) {
    return http.delete<void>(`/variations/${id}`)
  },
}
