<template>
  <div>
    <div class="query-param">
      <el-form status-icon ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px">
        <ElFormItem label="开始时间">
          <el-date-picker
            v-model="ruleForm.start"
            type="datetime"
            placeholder="选择开始时间"
            format="YYYY/MM/DD HH:mm:ss"
          />
        </ElFormItem>
        <ElFormItem label="结束时间">
          <el-date-picker
            v-model="ruleForm.end"
            type="datetime"
            placeholder="选择结束时间"
            format="YYYY/MM/DD HH:mm:ss"
          />
        </ElFormItem>
        <ElFormItem>
          <ElButton type="primary" @click="submitForm(ruleFormRef)" :loading="buttonLoading">查找</ElButton>
          <ElButton type="primary" @click="downloadKML">下载KML</ElButton>
        </ElFormItem>
      </el-form>
      <el-button type="danger" @click="clearGPSDatabase">清空数据库</el-button>
      <el-switch
        v-model="live"
        inline-prompt
        style="margin-left: 10px; --el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
        active-text="实时更新"
        inactive-text="关闭实时更新"
        @change="liveChange"
      />
    </div>

    <div class="live-data-info">
      <el-card v-if="live" style="margin-top: 10px">
        <div slot="header" class="clearfix">
          <span>实时数据 ({{ timestampDiffNow(liveData?.GPSTimestamp) }} 秒之前)</span>
        </div>
        <div>
          <p>经度: {{ liveData?.longitude }}</p>
          <p>纬度: {{ liveData?.latitude }}</p>
          <p>速度: {{ liveData?.speed }}</p>
          <p>海拔：{{ liveData?.altitude }}</p>
          <p>GPS时间: {{ timestampToUTC8(liveData?.GPSTimestamp) }}</p>
        </div>
      </el-card>
    </div>

    <div>
      <el-radio-group v-model="mapType" size="small">
        <el-radio-button label="标准" />
        <el-radio-button label="卫星图" />
      </el-radio-group>
    </div>
    <div id="map-container">
      <ElAmap :center="initMapOptions.center" :zoom="initMapOptions.zoom" @init="initMap">
        <el-amap-control-scale></el-amap-control-scale>
        <el-amap-control-tool-bar></el-amap-control-tool-bar>
        <el-amap-control-geolocation position="RT"></el-amap-control-geolocation>
        <el-amap-layer-satellite
          :visible="mapType === '卫星图' ? true : false"
          :opacity="0.8"
        ></el-amap-layer-satellite>

        <el-amap-marker
          :position="[
            liveData?.longitude ? liveData?.longitude : 113.3,
            liveData?.latitude ? liveData?.latitude : 23.3
          ]"
          :title="'北京市'"
        ></el-amap-marker>
      </ElAmap>
    </div>
  </div>
</template>

<script setup lang="ts">
import { BaseResponse } from "@/types/base"
import { GPSData } from "@/types/GPSData"
import { request } from "@/utils/request"
import {
  ElAmap,
  ElAmapControlGeolocation,
  ElAmapControlScale,
  ElAmapControlToolBar,
  ElAmapLayerSatellite,
  ElAmapMarker,
  gps84_To_gcj02
} from "@vuemap/vue-amap"
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus"
import { onMounted } from "vue"

interface RuleForm {
  start: Date
  end: Date
}
const currentMap = ref<any>(null)
const mapType = ref<string>("标准")
const buttonLoading = ref<boolean>(false)
const live = ref<boolean>(false)
const liveData = ref<GPSData>()
// 实时更新定时器
let liveTimer: any = null

const loading = (loading?: boolean) => {
  if (loading === undefined) {
    buttonLoading.value = !buttonLoading.value
    return
  }
  buttonLoading.value = loading
}

const ruleFormRef = ref<FormInstance>()
const ruleForm = ref<RuleForm>({
  // 开始时间比结束时间少一天
  start: new Date(new Date().getTime() - 24 * 60 * 60 * 1000),
  end: new Date()
})

const rules = reactive<FormRules<RuleForm>>({
  start: [{ type: "date", required: true, message: "请选择开始时间", trigger: "change" }],
  end: [{ type: "date", required: true, message: "请选择结束时间", trigger: "change" }]
})

const initMapOptions = ref<any>({
  zoom: 12,
  center: [116.397428, 39.90923]
})

const initMap = (map: any) => {
  currentMap.value = map
}

// 将 Date 转为秒级时间戳
const dateToTimestamp = (date: Date): number => {
  // 添加异常处理
  try {
    return Math.floor(date.getTime() / 1000)
  } catch (error) {
    console.error(error)
    return 0
  }
}

// 传入一个时间戳，计算和现在的差值
const timestampDiffNow = (timestamp: number | undefined): number => {
  if (!timestamp) {
    return 0
  }
  return Math.floor(Date.now() / 1000 - timestamp)
}

// 将时间戳转换为 UTC+8 时间字符串
const timestampToUTC8 = (timestamp: number | any): string => {
  return new Date(timestamp * 1000).toLocaleString("zh-CN", { timeZone: "Asia/Shanghai" })
}

// 传入结束和开始时间戳,请求接口获取数据
const fetchGPSData = async (start: number, end: number): Promise<GPSData[]> => {
  try {
    const res = await request<BaseResponse<GPSData[]>>({
      url: "/gps/data/",
      method: "get",
      params: {
        start_timestamp: start,
        end_timestamp: end
      }
    })
    let data = res.data.data
    if (data.length === 0) {
      return []
    }
    return res.data.data
  } catch (error) {
    ElMessage({
      type: "error",
      message: "请求失败"
    })
    return []
  }
}

// 传入 key 清除数据库全部数据
const clearAllGPSData = async (key: string) => {
  if (key === "") {
    ElMessage({
      type: "error",
      message: "请输入密钥"
    })
    return
  }
  try {
    let result = await request<BaseResponse<any>>({
      url: "/gps/rm/",
      method: "get",
      params: {
        key: key
      }
    })
    if (result.data.code !== 1) {
      ElMessage({
        type: "error",
        message: `清除失败${result.data.msg}`
      })
      return
    }
    ElMessage({
      type: "success",
      message: "清除成功"
    })
  } catch (error) {
    ElMessage({
      type: "error",
      message: "清除失败"
    })
  }
}

// 获取实时数据 接口 /gps/data/live/ 返回 BaseResponse<GPSData>
const getLiveGPSData = async (): Promise<GPSData | null> => {
  try {
    const res = await request<BaseResponse<GPSData>>({
      url: "/gps/live/",
      method: "get"
    })
    return res.data.data
  } catch (error) {
    ElMessage({
      type: "error",
      message: "实时数据请求失败"
    })
    return null
  }
}

const clearGPSDatabase = () => {
  ElMessageBox.prompt("请输入密钥", "清空 GPS 数据库", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    inputPattern: /\S/,
    inputErrorMessage: "密钥不能为空",
    type: "warning"
  })
    .then(({ value }) => {
      clearAllGPSData(value)
    })
    .catch(() => {
      ElMessage({
        type: "info",
        message: "取消清除"
      })
    })
}

// 在一个新窗口打开 kml 下载页面
const downloadKML = () => {
  let start = dateToTimestamp(ruleForm.value.start)
  let end = dateToTimestamp(ruleForm.value.end)
  if (start === 0 || end === 0) {
    ElMessage({
      type: "error",
      message: "时间格式错误"
    })
    return
  }
  window.open(`https://api.whaleluo.top/gps/data/kml/?start_timestamp=${start}&end_timestamp=${end}`)
}

// 传入GPSData数组,纠偏后绘图
const drawGPSData = (data: GPSData[]) => {
  let points = data.map((item) => {
    let result = gps84_To_gcj02(item.longitude, item.latitude)
    return [result["lng"], result["lat"]] as [number, number]
  })
  let polyline = new AMap.Polyline({
    path: points,
    borderWeight: 2, // 线条宽度，默认为 1
    strokeColor: "red", // 线条颜色
    lineJoin: "round" // 折线拐点的绘制样式
  })
  if (currentMap.value) {
    currentMap.value.add(polyline)
  }
}

const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  loading(true)
  await formEl.validate((valid, fields) => {
    if (valid) {
      console.log("submit!")
    } else {
      console.log("error submit!", fields)
    }
  })
  let start = dateToTimestamp(ruleForm.value.start)
  let end = dateToTimestamp(ruleForm.value.end)
  let data = await fetchGPSData(start, end)
  if (data.length === 0) {
    ElMessage({
      type: "error",
      message: "没有数据"
    })
    loading(false)
    return
  }
  drawGPSData(data)
  currentMap.value.setFitView()
  loading(false)
}

const setMapCenter = (longitude: number, latitude: number) => {
  if (currentMap.value) {
    currentMap.value.setZoomAndCenter(16, [longitude, latitude])
  }
}

// 开启实时更新后处理
const liveChange = (value: any) => {
  console.log(value)
  live.value = value
  // 每隔一秒获取一次实时数据
  const updateLive = (first: boolean = false) => {
    getLiveGPSData().then((res) => {
      if (res) {
        // correct gps data
        let result = gps84_To_gcj02(res.longitude, res.latitude)
        res.longitude = result["lng"]
        res.latitude = result["lat"]
        liveData.value = res
        if (first) {
          setMapCenter(res.longitude, res.latitude)
        }
      }
    })
  }

  if (live.value) {
    updateLive(true)
    liveTimer = setInterval(() => {
      updateLive()
    }, 1000)
  } else {
    clearInterval(liveTimer)
  }
}

onMounted(() => {})
</script>

<style scoped>
#map-container {
  overflow: hidden;
  padding: 0px;
  margin: 0px;
  margin-top: 8px;
  width: 100%;
  height: 80vh;
}

/* 加阴影加透明背景加圆角 */

.query-param {
  padding: 10px;
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}
</style>
