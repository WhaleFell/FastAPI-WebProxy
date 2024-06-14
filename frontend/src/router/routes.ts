// src/router/routes.ts 路由定义

import type { RouteRecordRaw } from "vue-router"

// icon
import { Radar, HomeTwo } from "@icon-park/vue-next"

const DashboardLayout = () => import("@/layout/dashboard.vue")

// define routes
const routes: Array<RouteRecordRaw> = [
    // login
    {
        path: "/",
        name: "index",
        redirect: { name: "login" },
    },
    {
        path: "/login",
        name: "login",
        component: () => import("@/views/login.vue"),
        meta: {
            title: "臺核中控",
        },
    },
    // dashboard routes
    {
        path: "/dashboard",
        component: DashboardLayout,
        meta: {
            title: "Dashboard",
        },
        children: [
            {
                path: "",
                name: "dashboard",
                component: () => import("@/components/Home.vue"),
                meta: {
                    title: "Home",
                    icon: HomeTwo,
                },
            },
            {
                path: "amap",
                name: "amap",
                component: () => import("@/components/GPSTrack.vue"),
                meta: {
                    title: "GPS Track",
                    icon: Radar,
                },
            },

        ]
    },
    // 404
    {
        path: "/:pathMatch(.*)*",
        name: "404",
        component: () => import("@/views/404.vue"),
    },

]

export default routes
