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

export interface VariationOptionPublic {
  id: number
  variation_id: number
  value: string
}

export interface VariationDropdownPublic {
  id: number
  name: string
  category_id?: number | null
  options: VariationOptionPublic[]
  selected_option_id?: number | null
}

export interface ProductImagePublic {
  id: number
  product_id: number
  url: string
  is_default: boolean
}

export interface ProductPublic extends ProductBase {
  id: number
  options: number[]
  images: ProductImagePublic[]
  variations: VariationDropdownPublic[]
}

export interface ProductListItem {
  id: number
  name: string
  price: number
  stock_qty: number
  sku?: string | null

  product_group_id: number
  category_id?: number | null
  default_image?: number | null

  options: number[]
}

export interface ProductListParams {
  offset?: number
  limit?: number
  category_id?: number
}
