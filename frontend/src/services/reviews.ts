import { http } from '../utils/http'
import type { ReviewCreate, ReviewPublic } from '../types/review'

export default {
  async getForProductGroup(productGroupId: number) {
    return http.get<ReviewPublic[]>(`/products/${productGroupId}/reviews`)
  },

  async getOne(reviewId: number) {
    return http.get<ReviewPublic>(`/reviews/${reviewId}`)
  },

  async create(data: ReviewCreate) {
    return http.post<ReviewPublic>('/reviews/', data)
  },

  async delete(reviewId: number) {
    return http.delete<void>(`/reviews/${reviewId}`)
  },
}
