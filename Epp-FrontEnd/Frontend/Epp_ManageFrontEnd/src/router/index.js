import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            redirect: '/home',
            component: () => import(`@/views/layout/LayoutContainer.vue`),
            children: [
                {
                    path: 'home',
                    component: () => import(`@/views/main/HomePage.vue`)
                },
                {
                    path: 'user',
                    component: () => import(`@/views/user/UserManage.vue`)
                },
                {
                    path: 'paper',
                    component: () => import(`@/views/paper/PaperManage.vue`)
                },
                {
                    path: 'report',
                    redirect: '/report/unhandled',
                    component: () => import(`@/views/report/ReportManage.vue`),
                    children: [
                        {
                            path: 'unhandled',
                            components: { comment: () => import(`@/views/report/UnhandledReport.vue`) }
                        },
                        {
                            path: 'handled',
                            components: { comment: () => import(`@/views/report/HandledReport.vue`) }
                        },
                        {
                            path: 'ai-review',
                            components: { ai: () => import('@/views/report/AIReview.vue')}
                        },
                        {
                            path: 'ai-reject',
                            components: { ai: () => import('@/views/report/AIReject.vue') }
                        },
                        {
                            path: 'annot-handled',
                            components: { annot: () => import('@/views/report/annotation/HandledReport.vue') }
                        },
                        {
                            path: 'annot-unhandled',
                            components: { annot: () => import('@/views/report/annotation/UnhandledReport.vue') }
                        }
                    ]
                }
            ]
        },
        {
            path: '/login',
            name: 'login',
            component: () => import(`@/views/login/index.vue`),
            meta: {
                title: '登录页'
            }
        }
    ]
})

router.beforeEach((to) => {
    if (!store.getters.isManagerLogin && to.path !== '/login') return '/login'
})

export default router
