<template>
  <div class="flex flex-wrap gap-3 justify-center">
    <div class="w-full text-center font-bold">{{ word }}</div>
    <div class="basis-full flex justify-center">
      <button class="btn btn-info" @click="logout()">Logout</button>
    </div>
    <div class="stats shadow">
      <div class="stat">
        <div class="stat-title">Media Query</div>
        <div class="stat-value flex gap-2">
          {{ mediaType }}
          <div class="grow smm:bg-purple-800 sm:bg-purple-600 md:bg-purple-400 lg:bg-purple-200 xl:bg-purple-50"></div>
        </div>
        <div class="stat-desc text-wrap">The color more deep means the screen size more large.</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { auth } from "@/utils/auth"
import { mediaType } from "@/utils/mediaQuery"
import { ElMessageBox } from "element-plus"
import { useRouter } from "vue-router"

const word = ref("Home")
const router = useRouter()

const logout = () => {
  ElMessageBox.confirm("Are you sure to logout?", "Logout", {
    confirmButtonText: "OK",
    cancelButtonText: "Cancel",
    type: "warning"
  })
    .then(() => {
      auth.logout()
      router.push({ name: "login" })
    })
    .catch(() => {
      console.log("cancel")
    })
}
</script>

<style scoped></style>
