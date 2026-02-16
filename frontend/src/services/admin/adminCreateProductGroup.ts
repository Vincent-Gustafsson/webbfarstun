import { http } from '@/utils/http'
import type {
  ProductGroup,
  ProductGroupCreate,
  ProductGroupUpdate,
} from '@/types/admin/adminCreateProductGroup'

export default {
  async getAll() {
    return http.get<ProductGroup[]>('/product-groups/')
  },

  async getOne(id: number) {
    return http.get<ProductGroup>(`/product-groups/${id}`)
  },

  async create(data: ProductGroupCreate) {
    return http.post<ProductGroup>('/product-groups/', data)
  },

  async update(id: number, data: ProductGroupUpdate) {
    return http.patch<ProductGroup>(`/product-groups/${id}`, data)
  },

  async delete(id: number) {
    return http.delete<ProductGroup>(`/product-groups/${id}`)
  },
}
