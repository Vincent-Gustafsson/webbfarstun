export interface Product {
  id: number
  name: string
  product_group_id: number
  price: number
  stock_qty: number
  description: string
  sku?: string
  default_image: string
}

export interface ProductCreate {
  name: string
  product_group_id: number
  price: number
  stock_qty: number
  description: string
  sku?: string
  options: number[]
  default_image: string
}

export interface ProductUpdate {
  name?: string
  product_group_id?: number
  price?: number
  stock_qty?: number
  description?: string
  sku?: string
  default_image?: string
}
