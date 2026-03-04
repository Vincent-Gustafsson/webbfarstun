import { http } from '@/utils/http'
import type {
  VariationOption,
  VariationOptionCreate,
  VariationOptionUpdate,
} from '@/types/admin/variationOption'

export default {
  async getAll() {
    return http.get<VariationOption[]>('/variation-options/')
  },

  async getOne(id: number) {
    return http.get<VariationOption>(`/variation-options/${id}`)
  },

  async create(data: VariationOptionCreate) {
    return http.post<VariationOption>('/variation-options/', data)
  },

  async update(id: number, data: VariationOptionUpdate) {
    return http.patch<VariationOption>(`/variation-options/${id}`, data)
  },

  async delete(id: number) {
    return http.delete<VariationOption>(`/variation-options/${id}`)
  },
}
