<template>
  <ElContainer class="h-[100vh]">
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
    <ElContainer class="h-[100vh] flex">
      <Aside :isCollapse="isCollapse" />
      <ElMain>
        <!-- router view -->
        <!-- VUE can only animate one element at a time, so always define an element at the first level of the template, it can be a "div" or a "span", whatever, usually a div -->
        <RouterView v-slot="{ Component }">
          <Transition name="moveL">
            <KeepAlive>
              <component :is="Component" />
            </KeepAlive>
          </Transition>
        </RouterView>
      </ElMain>
    </ElContainer>
  </ElContainer>
</template>

<script setup lang="ts">
import Aside from "@/components/Aside.vue"
import { MenuFoldOne, MenuUnfoldOne } from "@icon-park/vue-next"
import { onMounted } from "vue"

const isCollapse = ref<boolean>(false)

onMounted(() => {})
</script>

<style scoped>
.moveL-enter-active,
.moveL-leave-active {
  transition: all 0.3s linear;
  transform: translateX(0%);
}
.moveL-enter,
.moveL-leave {
  transform: translateX(-100%);
}
.moveL-leave-to {
  transform: translateX(-100%);
}
</style>
