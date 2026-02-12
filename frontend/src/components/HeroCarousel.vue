<script setup lang="ts">
const slides = [
  {
    id: 'b1',
    src: 'https://cdn.inet.se/img/1250x10000/cms/fe82a8de-b9fc-4b4c-87d6-ee9efe36cc58.jpeg',
    alt: 'Banner 1',
  },
  {
    id: 'b2',
    src: 'https://cdn.inet.se/img/1250x10000/cms/240b26a9-ee1d-4561-875b-32d51aba026d.jpeg',
    alt: 'Banner 2',
  },
  { id: 'b3', src: 'https://cdn.inet.se/youtube/858x483/raMruOUo_dU.jpg', alt: 'Banner 3' },
]
</script>

<template>
  <div class="w-full">
    <div class="carousel w-full rounded-box overflow-hidden shadow bg-base-100">
      <div v-for="(s, idx) in slides" :key="s.id" :id="s.id" class="carousel-item relative w-full">
        <!-- image only -->
        <img :src="s.src" :alt="s.alt" class="w-full h-44 md:h-64 object-cover" />

        <!-- DaisyUI arrows -->
        <div
          class="absolute left-5 right-5 top-1/2 flex -translate-y-1/2 transform justify-between"
        >
          <a
            class="btn btn-ghost btn-circle bg-transparent hover:bg-transparent active:bg-transparent border-none shadow-none"
            :href="`#${slides[(idx - 1 + slides.length) % slides.length].id}`"
          >
            ❮
          </a>
          <a
            class="btn btn-ghost btn-circle bg-transparent hover:bg-transparent active:bg-transparent border-none shadow-none"
            :href="`#${slides[(idx + 1) % slides.length].id}`"
          >
            ❯
          </a>
        </div>
      </div>
    </div>
  </div>
</template>
