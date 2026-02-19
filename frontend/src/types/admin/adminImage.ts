export interface ProductImage {
  id: number
  url: string
}

export interface ProductImageCreate {
  url: string
  product_id: number
}

export interface ProductImageUpdate {
  url?: string
}
