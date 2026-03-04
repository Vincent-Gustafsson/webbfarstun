export interface ProductImage {
  id: number
  url: string
  is_default: boolean
}

export interface ProductImageCreate {
  url: string
  product_id: number
  is_default?: boolean
}

export interface ProductImageUpdate {
  url?: string
  is_default?: boolean
}
