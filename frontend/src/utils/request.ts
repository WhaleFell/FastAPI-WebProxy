import axios from "axios"
import { AxiosResponse } from "axios"
import { InternalAxiosRequestConfig, AxiosError } from "axios"

export const request = axios.create({
    baseURL: "https://api.whaleluo.top/",
    timeout: 2000,
})

// 添加请求拦截器
request.interceptors.request.use(
    (axiosConfig: InternalAxiosRequestConfig) => {
        // 在发送请求之前做些什么

        return axiosConfig
    },
    (error) => {
        // 对请求错误做些什么
        return Promise.reject(error)
    }
)

// 添加响应拦截器
request.interceptors.response.use(
    (response: AxiosResponse) => {
        // 对响应数据做点什么
        // 成功响应数据

        return response
    },
    (error: AxiosError) => {
        console.log(error)
        if (error.response) {
            // 请求成功发出且服务器也响应了状态码，但状态代码超出了 2xx 的范围
        } else if (error.request) {
            // 请求已经成功发起，但没有收到响应
            // `error.request` 在浏览器中是 XMLHttpRequest 的实例，
            // 而在node.js中是 http.ClientRequest 的实例
        } else {
        }
        return Promise.reject(error)
    }
)
