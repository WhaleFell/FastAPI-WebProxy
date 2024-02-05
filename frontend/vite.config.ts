import path from "path"
import { defineConfig } from "vite"
import Vue from "@vitejs/plugin-vue"
import Icons from "unplugin-icons/vite"
import IconsResolver from "unplugin-icons/resolver"
import AutoImport from "unplugin-auto-import/vite"
import Components from "unplugin-vue-components/vite"
import { ElementPlusResolver } from "unplugin-vue-components/resolvers"

const PathSrc = path.resolve(__dirname, "src")

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        Vue(),
        AutoImport({
            // Auto import functions from Vue, e.g. ref, reactive, toRef...
            // 自动导入 Vue 相关函数，如：ref, reactive, toRef 等
            imports: ["vue"],

            // Auto import functions from Element Plus, e.g. ElMessage, ElMessageBox... (with style)
            // 自动导入 Element Plus 相关函数，如：ElMessage, ElMessageBox... (带样式)
            resolvers: [
                ElementPlusResolver(),

                // Auto import icon components
                // 自动导入图标组件
                IconsResolver({
                    prefix: "Icon",
                }),
            ],

            dts: path.resolve(PathSrc, "auto-imports.d.ts"),
        }),

        Components({
            resolvers: [
                // Auto register icon components
                // 自动注册图标组件
                IconsResolver({
                    enabledCollections: ["ep"],
                }),
                // Auto register Element Plus components
                // 自动导入 Element Plus 组件
                ElementPlusResolver(),
            ],

            dts: path.resolve(PathSrc, "components.d.ts"),
        }),

        Icons({
            autoInstall: true,
        }),
    ],
    resolve: {
        alias: {
            "@": PathSrc,
        },
    },
})
