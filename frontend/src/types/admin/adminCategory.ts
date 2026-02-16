export interface Category {
  id: number
  name: string
  description?: string
  category_parent_id?: number
  is_container: boolean
}

export interface CategoryCreate {
  id: number
  name: string
  description?: string
  category_parent_id?: number
  is_container: boolean
}

export interface CategoryUpdate {
  name?: string
  description?: string
  category_parent_id?: number
  is_container?: boolean
}
