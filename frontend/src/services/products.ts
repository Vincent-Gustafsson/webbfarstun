import { http } from '../utils/http'
import type {
  ProductCreate,
  ProductListItem,
  ProductListParams,
  ProductPublic,
  ProductUpdate,
} from '../types/product'

export const productImageUrl = (productImageId: number) =>
  `/api/product-images/${productImageId}/file`

export default {
  async getAll(params?: ProductListParams) {
    if (params && Object.keys(params).length > 0) {
      return http.getWithParams<ProductListItem[]>('/products/', params)
    }
    return http.get<ProductListItem[]>('/products/')
  },

  async getOne(id: number) {
    return http.get<ProductPublic>(`/products/${id}`)
  },

  async create(data: ProductCreate) {
    return http.post<ProductPublic>('/products/', data)
  },

  async update(id: number, data: ProductUpdate) {
    return http.patch<ProductUpdate>(`/products/${id}`, data)
    // if you later change backend to return ProductPublic, swap generic type
  },

  async delete(id: number) {
    return http.delete<void>(`/products/${id}`)
  },
}
