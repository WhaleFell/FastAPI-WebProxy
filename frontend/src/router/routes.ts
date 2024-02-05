// src/router/routes.ts 路由定义

import type { RouteRecordRaw } from "vue-router"

// define routes
const routes: Array<RouteRecordRaw> = [
    {
        path: "/",
        name: "home",
        component: () => import("@/components/Home.vue"),
        meta: {
            title: "Home",
        },
    },
    {
        path: "/gps-track",
        name: "GPSTrack",
        component: () => import("@/components/GPSTrack.vue"),
        meta: {
            title: "GPS Track",
        },
    },
    {
        path: "/:pathMatch(.*)*",
        name: "404",
        component: () => import("@/views/404.vue"),
    },
]

export default routes
