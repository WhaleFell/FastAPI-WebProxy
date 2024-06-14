<template>
  <ElAside
    width="auto"
    class="bg-slate-400 z-50"
    :class="{ absolute: isssm, hidden: isCollapse && isssm, 'h-full': isssm }"
  >
    <ElMenu :collapse="isCollapse" :collapse-transition="!isssm" class="el-menu-vertical-demo">
      <RouterLink v-for="(menu, index) in menus" :to="{ name: menu.name }">
        <ElMenuItem :index="index.toString()" class="bg-slate-50">
          <template #title>
            {{ menu.name }}
          </template>
          <!-- <Radar theme="outline" size="24" fill="#333" class="mx-2" /> -->
          <component :is="menu.meta?.icon" size="24" class="mx-2" />
        </ElMenuItem>
      </RouterLink>
    </ElMenu>
  </ElAside>
</template>

<script lang="ts" setup>
import routes from "@/router/routes"
import { mediaType } from "@/utils/mediaQuery"
import { ElMenuItem } from "element-plus"
import { toRefs } from "vue"
import { RouteRecordRaw, RouterLink } from "vue-router"

const props = defineProps<{ isCollapse: boolean }>()
const { isCollapse } = toRefs(props)
const isssm = computed(() => mediaType.value === "ssm")

const menus = routes
  .filter((route) => route.path === "/dashboard")
  .flatMap((route) => route.children) as unknown as RouteRecordRaw[]
</script>

<style scoped>
.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 10rem;
  min-height: auto;
}

/* animation about width change */
@keyframes w-change {
  to {
    width: 0%;
  }

  from {
    width: 100%;
  }
}
</style>
