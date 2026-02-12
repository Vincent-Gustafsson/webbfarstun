export interface Product {
  id: number
  name: string
  product_group_id: number
  price: number
  stock_qty: number
  description: string
  sku?: string
}

export interface ProductCreate {
  name: string
  product_group_id: number
  price: number
  stock_qty: number
  description: string
  sku?: string
  options: number[]
}

export interface ProductUpdate {
  name?: string
  product_group_id?: number
  price?: number
  stock_qty?: number
  description?: string
  sku?: string
}
