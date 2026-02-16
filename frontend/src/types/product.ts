export interface ProductBase {
  name: string
  product_group_id: number
  price: number
  stock_qty: number
  description: string
  sku?: string | null
}

export interface ProductCreate extends ProductBase {
  options: number[]
}

export interface ProductUpdate {
  name?: string
  product_group_id?: number
  price?: number
  stock_qty?: number
  description?: string
  sku?: string | null
}

export interface ProductPublic extends ProductBase {
  id: number
  options: number[]
}

export interface ProductListItem {
  id: number
  name: string
  price: number
  stock_qty: number
  sku?: string | null

  product_group_id: number
  category_id?: number | null

  options: number[]
}

export interface ProductListParams {
  offset?: number
  limit?: number
  category_id?: number
}
