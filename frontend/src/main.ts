import { createApp } from "vue"
import App from "./App.vue"
import router from "./router"
import "element-plus/dist/index.css"
import "element-plus/es/components/message/style/css"
// iconpark
import "@icon-park/vue-next/styles/index.css"
import { install } from "@icon-park/vue-next/es/all"

const app = createApp(App)
install(app)
app.use(router).mount("#app")
