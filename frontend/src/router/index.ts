import { createRouter, createWebHistory } from "vue-router"
import routes from "./routes"

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
})

// 路由守卫/钩子 hook
// 全局前置守卫 / 路由拦截
router.beforeEach((to, from) => {
    const { title } = to.meta
    document.title = (title as string) || "默认标题"

    // 判断登陆
    // const { isNoLogin } = to.meta
    // if (!isNoLogin) return '/login'
})

export default router
