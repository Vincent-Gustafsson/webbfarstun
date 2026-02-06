import type { Category, CategoryNode } from '../types/category'

export function buildCategoryTree(categories: Category[]): CategoryNode[] {
  const map = new Map<number, CategoryNode>()
  const roots: CategoryNode[] = []

  // 1. Initialize nodes with PrimeVue properties
  categories.forEach((cat) => {
    map.set(cat.id, {
      ...cat,
      children: [],

      // MAPPING LOGIC:
      key: String(cat.id), // PrimeVue expects a string key
    })
  })

  // 2. Connect children to parents (Same as before)
  categories.forEach((cat) => {
    const node = map.get(cat.id)!
    if (cat.category_parent_id) {
      const parent = map.get(cat.category_parent_id)
      if (parent) {
        parent.children.push(node)
      } else {
        roots.push(node)
      }
    } else {
      roots.push(node)
    }
  })

  return roots
}
