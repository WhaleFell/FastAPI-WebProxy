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
      <ElAside width="auto" :class="mediaType === 'ssm' ? 'hidden' : ''">
        <ElMenu :collapse="isCollapse" :collapse-transition="true" class="el-menu-vertical-demo">
          <RouterLink v-for="(menu, index) in menus" :to="{ name: menu.name }">
            <ElMenuItem :index="index.toString()">
              <template #title>
                {{ menu.name }}
              </template>
              <Radar theme="outline" size="12" fill="#333" class="mx-2" />
            </ElMenuItem>
          </RouterLink>
        </ElMenu>
      </ElAside>
      <ElMain>
        <RouterView></RouterView>
      </ElMain>
    </ElContainer>
  </ElContainer>
</template>

<script setup lang="ts">
import routes from "@/router/routes"
import { RouterLink } from "vue-router"
import { RouteRecordRaw } from "vue-router"
import { onMounted } from "vue"
import { ElMenuItem } from "element-plus"
import { MenuFoldOne, MenuUnfoldOne, Radar } from "@icon-park/vue-next"
import { mediaType } from "@/utils/mediaQuery"

const isCollapse = ref(false)

// watch(isCollapse, (newValue, oldValue) => {
//   console.log(`new: ${newValue} old: ${oldValue}`)
// })

const menus = routes
  .filter((route) => route.path === "/dashboard")
  .flatMap((route) => route.children) as unknown as RouteRecordRaw[]

onMounted(() => {})
</script>

<style scoped>
.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 10rem;
  min-height: 400px;
}
</style>
