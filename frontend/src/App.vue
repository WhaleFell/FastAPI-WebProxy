<template>
  <RouterView v-slot="{ Component }">
    <component :is="Component" />
  </RouterView>
</template>

<script setup lang="ts">
// import { auth } from "./utils/auth"

// onMounted(() => {
//   setInterval(() => {
//     console.log(auth.expireSalt(10))
//   }, 1000)
// })
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
