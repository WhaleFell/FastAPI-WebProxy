import { createApp } from "vue"
import App from "./App.vue"
import router from "./router"
import "element-plus/dist/index.css"
import "element-plus/es/components/message/style/css"
// iconpark
import "@icon-park/vue-next/styles/index.css"
import { install } from "@icon-park/vue-next/es/all"

// amap
import VueAMap, { initAMapApiLoader } from "@vuemap/vue-amap"
import "@vuemap/vue-amap/dist/style.css"

initAMapApiLoader({
    key: "1f34538dbd8ac8bb9e143f064ace341f",
    securityJsCode: "38e11e519ee47e9a746b9907a5a54620", // 新版key需要配合安全密钥使用
    //Loca:{
    //  version: '2.0.0'
    //} // 如果需要使用loca组件库，需要加载Loca
})

const app = createApp(App)
install(app)
app.use(router).use(VueAMap).mount("#app")
