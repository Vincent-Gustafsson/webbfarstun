export interface ProductGroup {
  id: number
  name: string
  category_id: number
}

export interface ProductGroupCreate {
  name: string
  category_id: number
}

export interface ProductGroupUpdate {
  name?: string
  category_id?: number
}
