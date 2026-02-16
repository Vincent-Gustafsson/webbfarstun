<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    /** Read-only: 0..5 (can be .5). Interactive: whole stars only (1..5). */
    modelValue?: number
    /** If true: user can select a rating (whole stars only). */
    interactive?: boolean
    disabled?: boolean

    /** Applied to the wrapper div (e.g. "rating-xs", "rating-lg") */
    sizeClass?: string
    /** Applied to each star input (e.g. "bg-green-500", "bg-warning") */
    bgClass?: string

    ariaLabel?: string
  }>(),
  {
    modelValue: 0,
    interactive: false,
    disabled: false,
    sizeClass: 'rating-md',
    bgClass: 'bg-warning',
    ariaLabel: 'Rating',
  },
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void
}>()

const name = `rating-${Math.random().toString(36).slice(2)}`

// Clamp & round to nearest 0.5 for display
const displayValue = computed(() => {
  const v = Number(props.modelValue ?? 0)
  if (!Number.isFinite(v)) return 0
  const clamped = Math.min(Math.max(v, 0), 5)
  return Math.round(clamped * 2) / 2
})

// We render 10 half-steps. Checked step is 0..10
const checkedStep = computed(() => {
  const v = props.interactive
    ? Math.min(Math.max(Math.round(Number(props.modelValue ?? 1)), 1), 5) // whole stars, min 1
    : displayValue.value

  return Math.round(v * 2) // 0..10
})

function setFromStep(stepIndex: number) {
  if (!props.interactive || props.disabled) return

  // whole stars only:
  // if user clicks a half-step (odd), snap to the next whole star (even).
  const snapped = stepIndex % 2 === 0 ? stepIndex : Math.min(stepIndex + 1, 10)
  emit('update:modelValue', snapped / 2)
}
</script>

<template>
  <div
    class="rating rating-half"
    :class="sizeClass"
    role="radiogroup"
    :aria-label="ariaLabel"
    :aria-readonly="interactive ? 'false' : 'true'"
  >
    <!-- DaisyUI pattern: hidden "0" -->
    <input type="radio" class="rating-hidden" :name="name" :checked="checkedStep === 0" disabled />

    <!-- 10 half-steps: 0.5, 1.0, 1.5, ... 5.0 -->
    <input
      v-for="stepIndex in 10"
      :key="stepIndex"
      type="radio"
      :name="name"
      class="mask mask-star-2"
      :class="[
        stepIndex % 2 === 1 ? 'mask-half-1' : 'mask-half-2',
        bgClass,
        // fade anything above the selected value (works for both readonly + interactive)
        stepIndex > checkedStep ? 'opacity-30' : '',
      ]"
      :aria-label="`${stepIndex / 2} star`"
      :checked="checkedStep === stepIndex"
      :disabled="!interactive || disabled"
      @change="setFromStep(stepIndex)"
    />
  </div>
</template>
