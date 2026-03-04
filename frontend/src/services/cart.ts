import { http } from '@/utils/http'
import type { ShoppingCartPublic, ShoppingCartItemCreateInCart } from '@/types/cart'

export default {
  async getCart() {
    return http.get<ShoppingCartPublic>('/cart/')
  },

  async addItem(data: ShoppingCartItemCreateInCart) {
    return http.post<ShoppingCartPublic>('/cart/items', data)
  },
}
