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

export const collectPaper = (paperId) => {
  return request({
    method: 'put',
    url: 'api/collectPaper',
    data: {
      paper_id: paperId
    }
  })
}

// export const fetchFurtherReadingPapers = (paperId) => {
//   return request({
//     method: 'get',
//     url: 'api/relatedPaper',
//     params: {
//       paper_id: paperId
//     }
//   })
// }
