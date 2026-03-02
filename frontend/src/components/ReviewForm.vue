<script setup lang="ts">
import { ref, computed } from 'vue'
import StarRating from '@/components/StarRating.vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isLoggedIn = computed(() => !!userStore.me)

const props = defineProps<{
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'submit', payload: { score: number; comment: string }): void
}>()

const rating = ref(1)
const comment = ref('')

function onSubmit() {
  emit('submit', { score: rating.value, comment: comment.value.trim() })
  comment.value = ''
  rating.value = 1
}
</script>

<template>
  <div class="flex justify-center items-center gap-4">
    <textarea v-model="comment" class="textarea w-4/5" placeholder="An optional comment" />

    <div class="flex flex-col gap-4">
      <StarRating v-model="rating" interactive size-class="rating-md" bg-class="bg-accent" />

      <div class="tooltip" :data-tip="isLoggedIn ? '' : 'You must be logged in to write a review'">
        <button
          class="btn btn-primary"
          type="button"
          :disabled="props.loading || !isLoggedIn"
          @click="onSubmit"
        >
          Submit
        </button>
      </div>
    </div>
  </div>
</template>
