<template>
  <div class="container mx-auto flex h-screen">
    <div class="m-auto size-auto space-y-3 rounded-xl bg-gray-200 p-7 shadow-lg">
      <p class="text-center text-xl">臺核中控</p>
      <input
        type="text"
        placeholder="Username"
        class="input block w-full text-center"
        v-model="username"
        required
        @keydown.enter="verify()"
      />
      <input
        type="password"
        placeholder="Password"
        class="input block w-full text-center"
        v-model="password"
        @keydown.enter="verify()"
      />
      <button class="btn btn-accent btn-wide" @click="verify()">
        <span class="loading loading-spinner" :class="{ hidden: !loading }"></span>Verify
      </button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { auth } from "@/utils/auth"
import { ElMessage } from "element-plus"
import { ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const username = ref<string>("admin")
const password = ref<string>("")
const loading = ref<boolean>(false)

const verify = () => {
  loading.value = true
  if (!username.value || !password.value) {
    ElMessage.error("Username and password are required")
    loading.value = false
    return
  }

  let res = auth.isLogined() || auth.login(username.value, password.value)
  if (res) {
    console.log("Login success")
    router.push({ name: "dashboard" })
  } else {
    ElMessage.error("Invalid username or password")
  }
  loading.value = false
}

onMounted(() => {
  if (auth.isLogined()) {
    ElMessage.success("Already logged in")
    router.push({ name: "dashboard" })
  }
})
</script>

<style scoped></style>
