import axios from 'axios'
// import { ElMessage } from 'element-plus'

// const serverURL = 'https://epp.buaase.cn'
const serverURL = 'http://114.116.205.43:8000'

const instance = axios.create({ baseURL: serverURL })

// instance.interceptors.response.use(
//     (res) => {
//         return res
//     },
//     (err) => {
//         ElMessage({ message: err.response.data.message })
//         console.log(err)
//         return Promise.reject(err)
//     }
// )

export default instance
export { serverURL }
