<template>
  <div class="common-layout">
    <ElContainer>

      <ElAside width="auto">
        <ElScrollbar>
          <el-menu :default-active="router.currentRoute.value.path" :collapse="isCollapse" router>
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

      <ElMain>
        <el-button @click="isCollapse = !isCollapse">
          <el-icon>
            <icon-park v-if="isCollapse" type="menu-fold-one" theme="filled" />
            <icon-park v-else type="menu-unfold-one" theme="filled" />
          </el-icon>
        </el-button>

        <router-view></router-view>
      </ElMain>
    </ElContainer>
  </div>
</template>

<script setup lang="ts">
import { IconPark } from '@icon-park/vue-next/es/all';
import router from './router';
const isCollapse = ref<boolean>(false);


</script>

<style scoped>
.common-layout {
  display: flex;
}
</style>
