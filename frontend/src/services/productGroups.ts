import { http } from '@/utils/http'
import type { ProductGroup, ProductGroupCreate } from '@/types/productGroup'

export default {
  async getAll() {
    return http.get<ProductGroup[]>('/product-groups/')
  },

  async create(data: ProductGroupCreate) {
    return http.post<ProductGroup>('/product-groups/', data)
  },

  async delete(id: number) {
    return http.delete<void>(`/product-groups/${id}`)
  },
}
