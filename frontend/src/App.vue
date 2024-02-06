<template>
  <div class="common-layout">
    <ElContainer>

      <ElAside :width="isCollapse ? '0px' : 'auto'">
        <ElScrollbar>
          <el-menu :default-active="router.currentRoute.value.path" :collapse="isCollapse" router close-on-click-outside>
            <el-menu-item index="/">
              <ElIcon>
                <icon-park type="home" theme="filled" />
              </ElIcon>
              <span>Home</span>
            </el-menu-item>

            <el-menu-item index="/gps-track">
              <ElIcon>
                <icon-park type="local" theme="filled" />
              </ElIcon>
              <span>GPS Track</span>
            </el-menu-item>
          </el-menu>

        </ElScrollbar>
      </ElAside>

      <ElContainer>
        <ElHeader height="auto" style="text-align: left; font-size: 12px">
          <el-button @click="isCollapse = !isCollapse">
            <el-icon>
              <icon-park v-if="isCollapse" type="menu-fold-one" theme="filled" />
              <icon-park v-else type="menu-unfold-one" theme="filled" />
            </el-icon>
          </el-button>
        </ElHeader>
        <ElMain>
          <router-view></router-view>
        </ElMain>
      </ElContainer>
    </ElContainer>
  </div>
</template>

<script setup lang="ts">
import { IconPark } from '@icon-park/vue-next/es/all';
import router from './router';
const isCollapse = ref<boolean>(false);


</script>

<style scoped>
.common-layout .el-header {
  position: relative;
  background-color: var(--el-color-primary-light-7);
  color: var(--el-text-color-primary);

}
</style>
