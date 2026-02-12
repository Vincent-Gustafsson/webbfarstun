import type { Category, CategoryNode } from '@/types/category'

export function buildCategoryTree(categories: Category[]): CategoryNode[] {
  const byId = new Map<number, CategoryNode>()

  // Create all nodes
  for (const c of categories) {
    byId.set(c.id, {
      ...c,
      key: `cat-${c.id}`,
      children: [],
    })
  }

  // Link children to parents
  const roots: CategoryNode[] = []
  for (const node of byId.values()) {
    const parentId = node.category_parent_id ?? null

    if (parentId == null) {
      roots.push(node)
      continue
    }

    const parent = byId.get(parentId)
    // If parent is missing (or self-parent), treat as root
    if (!parent || parentId === node.id) {
      roots.push(node)
      continue
    }

    parent.children.push(node)
  }

  // Optional: sort by name at every level (remove if you want API order)
  const sortRec = (nodes: CategoryNode[]) => {
    nodes.sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }))
    nodes.forEach((n) => sortRec(n.children))
  }
  sortRec(roots)

  return roots
}
