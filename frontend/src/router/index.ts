import { createRouter, createWebHashHistory } from "vue-router"
import { ElMessage } from "element-plus"

// NProgress
import NProgress from "nprogress"
import "nprogress/nprogress.css"

import routes from "./routes"
import { auth } from "@/utils/auth"

NProgress.configure({
    easing: "ease", // 动画方式
    speed: 500, // 递增进度条的速度
    showSpinner: false, // 是否显示加载 icon
    trickleSpeed: 200, // 自动递增间隔
    minimum: 0.3, // 初始化时的最小百分比
})

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

// 路由守卫/钩子 hook
// 全局前置守卫 / 路由拦截
router.beforeEach((to, _from) => {
    NProgress.start()
    // Change title
    const { title } = to.meta
    document.title = (title as string) || "default title"

    // handle login
    if (!auth.isLogined() && to.name !== "login") {
        console.log("Not logined")
        ElMessage.warning("Login required")
        return { name: "login" }
    }

})

router.afterEach(() => {
    NProgress.done()
})

export default router
