// api base types
export interface BaseResponse<T> {
    code: number
    msg: string
    data: T
}
