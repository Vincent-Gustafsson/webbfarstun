<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { themeChange } from 'theme-change'

const LIGHT = 'nord'
const DARK = 'business'

const theme = ref<string>(LIGHT)
const isDark = computed(() => theme.value === DARK)

// Bind the checkbox directly to your theme state
const darkChecked = computed<boolean>({
  get: () => isDark.value,
  set: (checked) => applyTheme(checked ? DARK : LIGHT),
})

function applyTheme(t: string) {
  // daisyUI reads this attribute (and it's a good fallback even with theme-controller)
  document.documentElement.setAttribute('data-theme', t)
  localStorage.setItem('theme', t)
  theme.value = t
}

onMounted(() => {
  // optional: keep theme-change happy if you use it elsewhere
  themeChange(false)

  const saved = localStorage.getItem('theme')
  applyTheme(saved === DARK ? DARK : LIGHT)
})
</script>

<template>
  <label class="toggle text-base-content">
    <input
      v-model="darkChecked"
      type="checkbox"
      class="theme-controller"
      :value="DARK"
      role="switch"
      :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
      :aria-checked="darkChecked"
    />

    <!-- sun -->
    <svg aria-label="sun" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <g
        stroke-linejoin="round"
        stroke-linecap="round"
        stroke-width="2"
        fill="none"
        stroke="currentColor"
      >
        <circle cx="12" cy="12" r="4"></circle>
        <path d="M12 2v2"></path>
        <path d="M12 20v2"></path>
        <path d="m4.93 4.93 1.41 1.41"></path>
        <path d="m17.66 17.66 1.41 1.41"></path>
        <path d="M2 12h2"></path>
        <path d="M20 12h2"></path>
        <path d="m6.34 17.66-1.41 1.41"></path>
        <path d="m19.07 4.93-1.41 1.41"></path>
      </g>
    </svg>

    <!-- moon -->
    <svg aria-label="moon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <g
        stroke-linejoin="round"
        stroke-linecap="round"
        stroke-width="2"
        fill="none"
        stroke="currentColor"
      >
        <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path>
      </g>
    </svg>
  </label>
</template>
