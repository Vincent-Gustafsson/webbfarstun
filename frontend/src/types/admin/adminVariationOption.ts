export interface VariationOption {
  id: number
  value: string
}

export interface VariationOptionCreate {
  value: string
  variation_id?: number
}

export interface VariationOptionUpdate {
  value?: string
  variation_id?: number
}
