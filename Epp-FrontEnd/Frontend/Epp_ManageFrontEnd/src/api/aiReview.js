import request from '@/utils/request.js'

export const getAIReviewAll = ({date, page_num, page_size}) => {
    return request({
        method: 'get',
        url: '/api/manage/autoCommentReports',
        params: {
            mode: 1,
            date,
            page_num,
            page_size
        }
    })
}

export const getAIReviewReject = ({date, page_num, page_size}) => {
    return request({
        method: 'get',
        url: '/api/manage/autoCommentReports',
        params: {
            mode: 2,
            date,
            page_num,
            page_size
        }
    })
}

export const getAIReviewDetail = (reviewId) => {
    return request({
        method: 'get',
        url: '/api/manage/autoCommentReportDetail',
        params: {
            review_id: reviewId
        }
    })
}