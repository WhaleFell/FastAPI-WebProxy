<template>
  <ElAside width="auto" :class="mediaType === 'ssm' ? 'hidden' : ''">
    <ElMenu :collapse="isCollapse" :collapse-transition="true" class="el-menu-vertical-demo">
      <RouterLink v-for="(menu, index) in menus" :to="{ name: menu.name }">
        <ElMenuItem :index="index.toString()" class="bg-slate-50">
          <template #title>
            {{ menu.name }}
          </template>
          <Radar theme="outline" size="12" fill="#333" class="mx-2" />
        </ElMenuItem>
      </RouterLink>
    </ElMenu>
  </ElAside>
</template>

<script lang="ts" setup>
import { ElMenuItem } from "element-plus"
import { mediaType } from "@/utils/mediaQuery"
import { Radar } from "@icon-park/vue-next"

// router
import { RouterLink } from "vue-router"
import routes from "@/router/routes"
import { RouteRecordRaw } from "vue-router"

const isCollapse = ref(false)

const menus = routes
  .filter((route) => route.path === "/dashboard")
  .flatMap((route) => route.children) as unknown as RouteRecordRaw[]
</script>

<style scoped></style>
