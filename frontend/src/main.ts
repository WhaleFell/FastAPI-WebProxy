import { createApp } from "vue"
import App from "./App.vue"
import router from "./router"
// tailwind css
import "./style.css"

// element-plus css
import "element-plus/dist/index.css"

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

// Pinia
import { createPinia } from "pinia"
const pinia = createPinia()


const app = createApp(App)
app.use(router)
    .use(VueAMap)
    .use(pinia)
    .mount("#app")
