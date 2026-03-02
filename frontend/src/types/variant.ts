export type OptionAvailability = {
  variation_id: number
  variation_name: string
  option_id: number
  option_value: string
  available: boolean
}

export type AvailabilityRequest = {
  selected_option_ids: number[]
}

export type ResolveRequest = {
  selected_option_ids: number[]
}

export type ResolveResponse = {
  product_id: number | null
}
