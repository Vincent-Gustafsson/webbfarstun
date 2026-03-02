import { defineStore } from 'pinia'
import reviewService from '@/services/reviews'
import type { ReviewCreate, ReviewPublic } from '@/types/review'
import { getErrorMessage } from '@/utils/error'

type ReviewState = {
  byProductGroup: Record<number, ReviewPublic[]>
  activeProductGroupId: number | null
  loading: boolean
  error: string | null
}

export const useReviewStore = defineStore('review', {
  state: (): ReviewState => ({
    byProductGroup: {},
    activeProductGroupId: null,
    loading: false,
    error: null,
  }),

  getters: {
    activeReviews(state): ReviewPublic[] {
      if (state.activeProductGroupId == null) return []
      return state.byProductGroup[state.activeProductGroupId] ?? []
    },

    getForProductGroup: (state) => (productGroupId: number) =>
      state.byProductGroup[productGroupId] ?? [],
  },

  actions: {
    clearError() {
      this.error = null
    },

    setActiveProductGroup(productGroupId: number | null) {
      this.activeProductGroupId = productGroupId
    },

    setForProductGroup(productGroupId: number, reviews: ReviewPublic[]) {
      this.byProductGroup[productGroupId] = reviews
    },

    upsertIntoProductGroup(productGroupId: number, review: ReviewPublic) {
      const list = this.byProductGroup[productGroupId] ?? (this.byProductGroup[productGroupId] = [])
      const i = list.findIndex((r) => r.id === review.id)
      if (i === -1) list.unshift(review)
      else list[i] = review
    },

    removeFromProductGroup(productGroupId: number, reviewId: number) {
      const list = this.byProductGroup[productGroupId]
      if (!list) return
      this.byProductGroup[productGroupId] = list.filter((r) => r.id !== reviewId)
    },

    async fetchForProductGroup(productGroupId: number, opts?: { force?: boolean }) {
      this.loading = true
      this.error = null
      this.activeProductGroupId = productGroupId

      try {
        if (!opts?.force && this.byProductGroup[productGroupId]) {
          return this.byProductGroup[productGroupId]
        }

        const reviews = await reviewService.getForProductGroup(productGroupId)
        this.setForProductGroup(productGroupId, reviews)
        return reviews
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
        return []
      } finally {
        this.loading = false
      }
    },

    async create(payload: ReviewCreate) {
      this.loading = true
      this.error = null
      try {
        const created = await reviewService.create(payload)
        this.upsertIntoProductGroup(created.product_group_id, created)
        return created
      } catch (err: unknown) {
        this.error = getErrorMessage(err)
        console.error(err)
        return null
      } finally {
        this.loading = false
      }
    },

    async remove(reviewId: number) {
      // optimistic remove
      const snapshot = JSON.parse(JSON.stringify(this.byProductGroup)) as Record<
        number,
        ReviewPublic[]
      >

      try {
        // best-effort: remove from whichever group contains it
        for (const [pgIdStr, list] of Object.entries(this.byProductGroup)) {
          const pgId = Number(pgIdStr)
          if (list.some((r) => r.id === reviewId)) {
            this.removeFromProductGroup(pgId, reviewId)
            break
          }
        }

        await reviewService.delete(reviewId)
      } catch (err: unknown) {
        this.byProductGroup = snapshot
        this.error = getErrorMessage(err) || 'Failed to delete review'
        console.error(err)
      }
    },
  },
})
