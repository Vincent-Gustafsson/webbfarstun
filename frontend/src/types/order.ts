export interface Order {
  id: number
  user_id: number
  product_id: number | null
  order_nr: number
  qty: number
  unit_price: number
  line_total: number
  product_name: string
  product_sku: string | null
  default_image: number | null
  purchased_at: string
}
