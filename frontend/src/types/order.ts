export interface Order {
  id: number
  user_id: number
  order_nr: number
  qty: number
  unit_price: number
  line_total: number
  product_name: string
  default_image: number | null
  purchased_at: string
}
