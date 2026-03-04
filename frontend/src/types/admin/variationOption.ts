export interface VariationOption {
  id: number
  value: string
  variation_id?: number
}

export interface VariationOptionCreate {
  value: string
  variation_id?: number
}

export interface VariationOptionUpdate {
  value?: string
  variation_id?: number
}
