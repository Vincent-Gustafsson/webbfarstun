import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), vueDevTools(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: true,
    port: 5173,
    allowedHosts: ['shop.vinlaro.com'],
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: 'https://api.vinlaro.com', // Points to the external API
        changeOrigin: true, // Required for external hosts
        secure: true, // Validates SSL
        rewrite: (path) => path.replace(/^\/api/, ''), // Removes /api prefix
      },
    },
  },
})
