import { http } from '@/utils/http'
import type { ProductImage, ProductImageCreate, ProductImageUpdate } from '@/types/admin/adminImage'

export default {
  async getAll() {
    return http.get<ProductImage[]>('/product-images/')
  },

  async getOne(id: number) {
    return http.get<ProductImage>(`/product-images/${id}`)
  },

  async create(data: ProductImageCreate) {
    return http.post<ProductImage>('/product-images/', data)
  },

  async update(id: number, data: ProductImageUpdate) {
    return http.patch<ProductImage>(`/product-images/${id}`, data)
  },

  async delete(id: number) {
    return http.delete<void>(`/product-images/${id}`)
  },

  async uploadProductImage(productId: number, file: File) {
    const fd = new FormData()
    fd.append('product_id', String(productId))
    fd.append('image', file)

    return http.postMultipart<ProductImage>('/product-images/upload', fd)
  },
}
