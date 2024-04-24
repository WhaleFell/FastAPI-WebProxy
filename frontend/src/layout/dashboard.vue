<template>
  <ElContainer>
    <ElHeader height="auto" class="flex content-center items-center justify-start bg-gray-300">
      <!-- collapse btn -->
      <label class="btn swap swap-rotate btn-sm my-2">
        <!-- this hidden checkbox controls the state -->
        <input type="checkbox" v-model="isCollapse" />
        <!-- hamburger icon -->
        <MenuFoldOne theme="outline" size="24" fill="#333" class="swap-off fill-current" />
        <!-- close icon class="swap-on fill-current" -->
        <MenuUnfoldOne theme="outline" size="24" fill="#333" class="swap-on fill-current" />
      </label>
      <p class="w-full truncate text-center text-3xl font-bold">Dome - 臺灣核電羣控</p>
    </ElHeader>
    <ElContainer>
      <ElMain>
        <RouterView></RouterView>
      </ElMain>
    </ElContainer>
  </ElContainer>
</template>

<script setup lang="ts">
import { onMounted } from "vue"

import { MenuFoldOne, MenuUnfoldOne } from "@icon-park/vue-next"

// watch(isCollapse, (newValue, oldValue) => {
//   console.log(`new: ${newValue} old: ${oldValue}`)
// })

onMounted(() => {})
</script>

<style scoped>
.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 10rem;
  min-height: auto;
}
</style>
