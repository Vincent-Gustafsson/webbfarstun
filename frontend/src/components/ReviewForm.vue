<script setup lang="ts">
import { ref } from 'vue'
import StarRating from '@/components/StarRating.vue'

const rating = ref(1)
const comment = ref('')
</script>

<template>
  <div class="flex justify-center items-center gap-4">
    <textarea v-model="comment" class="textarea w-4/5" placeholder="An optional comment" />

    <div class="flex flex-col gap-4">
      <StarRating v-model="rating" interactive size-class="rating-md" bg-class="bg-accent" />
      <button class="btn btn-primary" type="button">Submit</button>
    </div>
  </div>
</template>
