import { http } from '@/utils/http'
import type {
  ShoppingCartPublic,
  ShoppingCartItemCreateInCart,
  ShoppingCartItemUpdate,
} from '@/types/cart'

export default {
  async getCart() {
    return http.get<ShoppingCartPublic>('/cart/')
  },

  async addItem(data: ShoppingCartItemCreateInCart) {
    return http.post<ShoppingCartPublic>('/cart/items', data)
  },

  async removeItem(itemId: number) {
    return http.delete<void>(`/cart/items/${itemId}`)
  },

  async updateItemQty(itemId: number, data: ShoppingCartItemUpdate) {
    return http.patch<void>(`/cart/items/${itemId}`, data)
  },

  async clearCart() {
    return http.delete<void>('/cart/')
  },
}
