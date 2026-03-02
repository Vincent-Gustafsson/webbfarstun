<script setup lang="ts">
import { computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import ReviewForm from '@/components/ReviewForm.vue'
import StarRating from '@/components/StarRating.vue'
import { useProductStore } from '@/stores/products'
import { useReviewStore } from '@/stores/reviews'
import { useUserStore } from '@/stores/user'

const productStore = useProductStore()
const { activeProduct } = storeToRefs(productStore)

const reviewStore = useReviewStore()
const { activeReviews, loading, error } = storeToRefs(reviewStore)

const productGroupId = computed(() => activeProduct.value?.product_group_id ?? null)

const userStore = useUserStore()
const userId = computed(() => userStore.me?.id ?? null)

async function submitReview(payload: { score: number; comment: string }) {
  if (productGroupId.value == null) return

  await reviewStore.create({
    product_group_id: productGroupId.value,
    score: payload.score,
    comment: payload.comment,
  })
}

watch(
  productGroupId,
  async (pgId) => {
    if (pgId == null) return
    await reviewStore.fetchForProductGroup(pgId)
  },
  { immediate: true },
)
</script>

<template>
  <div class="w-full card bg-base-100 shadow p-4">
    <ReviewForm :loading="reviewStore.loading" @submit="submitReview" />

    <div class="divider"></div>

    <div class="flex items-center justify-between">
      <div class="text-xs opacity-60 tracking-wide">All reviews</div>
      <button
        class="btn btn-ghost btn-sm"
        type="button"
        :disabled="loading || productGroupId == null"
        @click="productGroupId && reviewStore.fetchForProductGroup(productGroupId, { force: true })"
      >
        Refresh
      </button>
    </div>

    <div v-if="loading" class="mt-3">
      <div class="skeleton h-6 w-full mb-2"></div>
      <div class="skeleton h-6 w-full mb-2"></div>
      <div class="skeleton h-6 w-full"></div>
    </div>

    <div v-else-if="error" class="alert alert-error mt-3">
      <span>{{ error }}</span>
    </div>

    <div v-else-if="activeReviews.length === 0" class="mt-3 text-sm opacity-70">
      No reviews yet.
    </div>

    <ul v-else class="list mt-3">
      <li v-for="r in activeReviews" :key="r.id" class="list-row">
        <div class="list-col-grow min-w-0">
          <div class="flex gap-2">
            <div class="font-semibold">{{ r.user.name }}</div>
            <StarRating :model-value="r.score" size-class="rating-xs" bg-class="bg-accent" />
          </div>

          <div class="text-sm opacity-80">
            {{ r.comment }}
          </div>
        </div>

        <button
          @click="reviewStore.remove(r.id)"
          v-if="r.user.id === userId"
          :disabled="loading"
          class="btn btn-sm btn-error justify-self-end"
        >
          Delete
        </button>
      </li>
    </ul>
  </div>
</template>
