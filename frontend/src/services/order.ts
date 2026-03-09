import { http } from '@/utils/http'
import type { Order } from '@/types/order'

export default {
  async getOrders(userId: number) {
    return http.get<Order[]>(`/orders/${userId}`)
  },
}
