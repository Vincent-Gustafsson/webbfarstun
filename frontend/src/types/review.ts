export type ReviewBase = {
  score: number
  comment: string
}

export type ReviewCreate = ReviewBase & {
  product_group_id: number
}

export type ReviewPublic = ReviewBase & {
  id: number
  product_group_id: number
  user: {
    name: string
    id: number
  }
}
