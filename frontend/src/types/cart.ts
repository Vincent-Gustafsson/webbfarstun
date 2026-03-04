export interface ShoppingCartItemPublic {
  id: number
  name: string
  image_id: number | null
  price: number
  stock_qty: number
  cart_qty: number
}

export interface ShoppingCartPublic {
  items: ShoppingCartItemPublic[]
}

export interface ShoppingCartItemCreateInCart {
  product_id: number
  qty: number
}

export interface ShoppingCartItemUpdate {
  qty: number
}
