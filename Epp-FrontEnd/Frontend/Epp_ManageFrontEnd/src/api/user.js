import request from '@/utils/request.js'

export const userLogin = ({ username, password }) => {
    return request({
        method: 'post',
        url: '/api/login',
        data: {
            username: username,
            userpassword: password
        }
    })
}

export const getUserProfile = (username) => {
    return request({
        method: 'get',
        url: '/api/manage/userProfile',
        params: {
            username: username
        }
    })
}

export const getUserList = ({ keyword, page_num, page_size }) => {
    return request({
        method: 'get',
        url: '/api/manage/users',
        params: {
            keyword,
            page_num,
            page_size
        }
    })
}

export const getUserOverviewStatistic = () => {
    return request({
        method: 'get',
        url: '/api/manage/userStatistic',
        params: {
            mode: 1
        }
    })
}

export const getUserMonthlyStatistic = () => {
    return request({
        method: 'get',
        url: '/api/manage/userStatistic',
        params: {
            mode: 2
        }
    })
}

export const getSearchWordsStatistic = () => {
    return request({
        method: 'get',
        url: '/api/manage/searchWordStatistic',
        params: {
            mode: 1
        }
    })
}

export const getAIQuestionsStatistic = () => {
    return request({
        method: 'get',
        url: '/api/manage/aiQuestionStatistic',
        params: {
            mode: 1
        }
    })
}

export const getUserActiveOption = () => {
    return request({
        method: 'get',
        url: '/api/manage/userActiveOption',
        params: {
            mode: 1
        }
    })
}