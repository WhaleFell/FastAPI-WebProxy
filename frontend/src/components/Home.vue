<template>
  <div>{{ word }}</div>
  <button class="btn btn-info" @click="logout()">Logout</button>
  <p>Media Query: {{ mediaType }}</p>
  <div
    class="ssm:bg-purple-900 size-[10vh] bg-black sm:bg-purple-600 md:bg-purple-400 lg:bg-purple-200 xl:bg-purple-50"
  ></div>
</template>

<script setup lang="ts">
import { auth } from "@/utils/auth"
import { ElMessageBox } from "element-plus"
import { useRouter } from "vue-router"
import { mediaType } from "@/utils/mediaQuery"

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
