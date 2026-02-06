export interface Category {
  id: number
  name: string
  description?: string | null
  category_parent_id?: number | null
  is_container: boolean
}

export interface CategoryCreate {
  name: string
  description?: string | null
  category_parent_id?: number | null
  is_container?: boolean
}

export interface CategoryUpdate {
  name?: string
  description?: string | null
  category_parent_id?: number | null
  is_container?: boolean
}

export interface CategoryNode extends Category {
  key: string
  children: CategoryNode[]
}
