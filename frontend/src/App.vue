<script setup lang="ts">
import { onMounted } from 'vue'
import { themeChange } from 'theme-change'

onMounted(() => themeChange(false))
</script>

<template>
  <header>
    <div class="wrapper"></div>
  </header>

  <RouterView />
</template>
