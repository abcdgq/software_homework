import request from '../request/request'

export const translateAbstract = (paperId) => {
  return request({
    method: 'get',
    url: 'api/paper/translate_abstract',
    params: {
      paper_id: paperId
    }
  })
}
