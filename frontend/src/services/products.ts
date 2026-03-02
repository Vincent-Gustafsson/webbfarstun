import { http } from '../utils/http'
import type {
  ProductCreate,
  ProductListItem,
  ProductListParams,
  ProductPublic,
  ProductUpdate,
} from '../types/product'

import type {
  AvailabilityRequest,
  OptionAvailability,
  ResolveRequest,
  ResolveResponse,
} from '../types/variant'

export const productImageUrl = (productImageId: number) => {
  if (!productImageId) return null
  return `/api/product-images/${productImageId}/file`
}

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

  async getAvailability(productGroupId: number, selectedOptionIds: number[]) {
    const payload: AvailabilityRequest = { selected_option_ids: selectedOptionIds }
    return http.post<OptionAvailability[]>(
      `/product-groups/${productGroupId}/availability`,
      payload,
    )
  },

  async resolveProduct(productGroupId: number, selectedOptionIds: number[]) {
    const payload: ResolveRequest = { selected_option_ids: selectedOptionIds }
    return http.post<ResolveResponse>(`/product-groups/${productGroupId}/resolve`, payload)
  },
}
