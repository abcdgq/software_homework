import axios from 'axios'

const serverUrl = 'http://127.0.0.1:8000'
const instance = axios.create({baseURL: serverUrl})

export const translateAbstract = (paperId) => {
  return instance({
    method: 'get',
    url: '',
    params: {
      paper_id: paperId
    }
  })
}
