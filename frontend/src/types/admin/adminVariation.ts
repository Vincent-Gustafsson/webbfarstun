export interface Variation{
  id: number
  category_id: number
  name: string
}

export interface VariationCreate{
  name: string
  category_id?: number
}

export interface VariationUpdate{
  name: string
}

