<template>
    <el-collapse v-model="isClsActive">
        <el-collapse-item name="1">
            <template #title>
                <div class="collapse-title">
                    <el-icon><i-ep-EditPen /></el-icon>
                    <span class="collapse-title-text">评论举报审核</span>
                </div>
            </template>
            <el-menu :default-active="commentTab" class="menu" mode="horizontal" :ellipsis="false" @select="commentTab=$event">
                <el-menu-item class="menu-content" index="unhandled">未审核</el-menu-item>
                <el-menu-item class="menu-content" index="handled">已审核</el-menu-item>
            </el-menu>
            <div style="padding: 10px">
                <component :is="commentTabComponent" />
            </div>
        </el-collapse-item>

        <!-- 新增的AI审核部分 -->
        <el-collapse-item name="2">
            <template #title>
                <div class="collapse-title">
                    <el-icon><i-ep-Cpu /></el-icon>
                    <span class="collapse-title-text">AI审核评论</span>
                </div>
            </template>
            <el-menu :default-active="aiTab" class="menu" mode="horizontal" :ellipsis="false" @select="aiTab=$event">
                <el-menu-item class="menu-content" index="review">全部审核内容</el-menu-item>
                <el-menu-item class="menu-content" index="reject">未通过内容</el-menu-item>
            </el-menu>
                <div style="padding: 10px">
                    <component :is="aiTabComponent" />
                </div>
        </el-collapse-item>

        <!-- 新增批注审核 -->
        <el-collapse-item name="3">
            <template #title>
                <div class="collapse-title">
                    <el-icon><i-ep-ChatLineSquare /></el-icon>
                    <span class="collapse-title-text">批注举报审核</span>
                </div>
            </template>
            <el-menu :default-active="annotTab" class="menu" mode="horizontal" :ellipsis="false" @select="annotTab=$event">
                <el-menu-item class="menu-content" index="unhandled">未审核</el-menu-item>
                <el-menu-item class="menu-content" index="handled">已审核</el-menu-item>
            </el-menu>
            <div style="padding: 10px">
                <component :is="annotTabComponent" />
            </div>
        </el-collapse-item>
    </el-collapse>
</template>

<script>
import HandledReport from '@/views/report/HandledReport.vue'
import UnhandledReport from '@/views/report/UnhandledReport.vue'
import AIReview from '@/views/report/AIReview.vue'
import AIReject from '@/views/report/AIReject.vue'
import AnnotReportHandled from '@/views/report/annotation/HandledReport.vue'
import AnnotReportUnhandled from '@/views/report/annotation/UnhandledReport.vue'
export default {
    components: {
        HandledReport, UnhandledReport,
        AIReview, AIReject,
        AnnotReportHandled, AnnotReportUnhandled
    },
    props: {},
    data() {
        return {
            isClsActive: ['1'],

            commentTab: 'unhandled',
            aiTab: 'review',
            annotTab: 'unhandled'
        }
    },
    watch: {},
    computed: {
        commentTabComponent() {
            return this.commentTab === 'unhandled'?
                'UnhandledReport' : 'HandledReport'
        },
        aiTabComponent() {
            return this.aiTab === 'review'?
                'AIReview' : 'AIReject'
        },
        annotTabComponent() {
            return this.annotTab === 'unhandled'?
                'AnnotReportUnhandled' : 'AnnotReportHandled'
        }
    },
    methods: {},
    created() {},
    mounted() {}
}
</script>
<style lang="scss" scoped>
.collapse-title {
    display: flex;
    align-items: center;
    color: rgb(0, 0, 0, 0.6);
    font-size: 16px;
    font-weight: bold;
    padding: 10px;
    .collapse-title-text {
        margin-left: 10px;
    }
}
.menu {
    margin: 0 10px;
    .menu-content {
        font-weight: bold;
        color: #909399;
    }
}
</style>
