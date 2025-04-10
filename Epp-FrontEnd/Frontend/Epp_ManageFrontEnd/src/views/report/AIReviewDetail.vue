<template>
    <div style="padding: 5px">
        <div class="report-card">
            <el-card class="review-card" shadow="hover">
                <div class="review-content">
                    <div class="comment">
                        <el-descriptions title="评论信息" :column="1" border>
                            <el-descriptions-item label="评论用户">
                                {{ aiReviewData.comment.user.user_name }}
                            </el-descriptions-item>
                            <el-descriptions-item label="评论日期">
                                {{ aiReviewData.comment.date }}
                            </el-descriptions-item>
                            <el-descriptions-item label="评论内容">
                                {{ aiReviewData.comment.content }}
                            </el-descriptions-item>
                        </el-descriptions>
                        <el-divider></el-divider>

                        <el-descriptions title="相关论文" :column="1" border>
                            <el-descriptions-item label="论文ID">
                                {{ aiReviewData.comment.paper.paper_id }}
                            </el-descriptions-item>
                            <el-descriptions-item label="论文标题">
                                {{ aiReviewData.comment.paper.title }}
                            </el-descriptions-item>
                        </el-descriptions>
                    </div>

                    <div class="review">
                        <el-descriptions title="审核结果" :column="1" border>
                            <el-descriptions-item label="是否通过">
                                {{ aiReviewData.isPassed }}
                            </el-descriptions-item>
                            <el-descriptions-item label="审核日期">
                                {{ aiReviewData.date }}
                            </el-descriptions-item>
                            <el-descriptions-item label="审核意见">
                                {{ aiReviewData.reason }}
                            </el-descriptions-item>
                        </el-descriptions>
                    </div>
                </div>
            </el-card>

            <!--            <div class="report-judge">-->
            <!--                <div class="report-judge-header">举报审核</div>-->
            <!--                <div style="padding: 16px">-->
            <!--                    <el-input-->
            <!--                        v-model="judgment.text"-->
            <!--                        style="width: 100%; min-height: 50%"-->
            <!--                        :autosize="{ minRows: 10, maxRows: 20 }"-->
            <!--                        type="textarea"-->
            <!--                        placeholder="请输入反馈意见"-->
            <!--                        maxlength="200"-->
            <!--                        show-word-limit-->
            <!--                    />-->
            <!--                    <div style="margin-top: 20px">-->
            <!--                        <span>屏蔽评论</span>-->
            <!--                        <el-switch-->
            <!--                            v-model="judgment.unvisibility"-->
            <!--                            style="margin-left: 10px; &#45;&#45;el-switch-on-color: #13ce66; &#45;&#45;el-switch-off-color: #d0d0d0"-->
            <!--                        />-->
            <!--                    </div>-->

            <!--                    <div style="margin-top: 20px">-->
            <!--                        <el-button-->
            <!--                            v-if="reportData.processed"-->
            <!--                            class="button"-->
            <!--                            type="primary"-->
            <!--                            round-->
            <!--                            style="margin: 0 auto"-->
            <!--                            @click="handleSubmit"-->
            <!--                        >-->
            <!--                            确认修改-->
            <!--                        </el-button>-->
            <!--                        <el-button-->
            <!--                            v-else-->
            <!--                            class="button"-->
            <!--                            type="primary"-->
            <!--                            round-->
            <!--                            style="margin: 0 auto"-->
            <!--                            @click="handleSubmit"-->
            <!--                        >-->
            <!--                            确认提交-->
            <!--                        </el-button>-->
            <!--                    </div>-->
            <!--                </div>-->
            <!--            </div>-->
        </div>
    </div>
</template>

<script>
import {getReportDetail, judgeReport} from '@/api/report'
import {ElMessage} from 'element-plus'
import AIReview from "./AIReview.vue";

export default {
    components: {},
    props: {reviewID: Number},
    data() {
        return {
            aiReviewData: {
                id: 10,
                comment: {
                    comment_id: '',
                    user: {
                        user_id: '',
                        user_name: ''
                    },
                    paper: {
                        paper_id: '',
                        title: ''
                    },
                    date: '', // 评论日期
                    content: '', // 评论内容
                    visibility: false // 评论是否被屏蔽
                },

                comment_level: 1, // 评论级别（原有）
                date: '', // ai审核日期
                isPassed: '', // 是否通过
                reason: '', // ai审核意见
            },
        }
    },
    watch: {
        reviewID: {
            handler() {
                this.draw()
            },
            immediate: true,
            deep: true
        }
    },
    computed: {},
    methods: {
        async draw() {
            await getReportDetail(this.$props.reviewID)
                .then((response) => {
                    this.aiReviewData = response.data
                    this.judgment.text = response.data.judgment
                    this.judgment.unvisibility = !response.data.comment.visibility
                })
                .catch((error) => {
                    ElMessage.error(error.response.data.message)
                })
        },
        // async handleSubmit() {
        //     await judgeReport({
        //         report_id: this.$props.reportID,
        //         text: this.judgment.text,
        //         visibility: !this.judgment.unvisibility
        //     })
        //         .then((response) => {
        //             ElMessage.success(response.data.message)
        //         })
        //         .catch((error) => {
        //             ElMessage.error(error.response.data.message)
        //         })
        // }
    }
}
</script>

<style lang="scss" scoped>
.review-content {
    display: flex;
    justify-content: space-between;
    gap: 24px;
    padding: 20px;
    border: 0px !important;
    border-right: 1px solid #dbdbdb !important;
    border-radius: 0px !important;
    background-color: #fff;

    .comment,
    .review {
        flex: 1;
        flex-direction: column;
    }

    .comment {
        max-width: 50%;
    }
    .review {
        max-width: 60%;
        height: 100%;  /* 确保审核结果部分占满父容器的高度 */
        display: flex;
        flex-direction: column;
        justify-content: space-between; /* 确保内容被拉伸填满 */
    }

    :deep(.review-card) {
        height: 100%;
        display: flex;
        flex-direction: column;
    }
}


:deep(.el-descriptions__label) {
    width: 20% !important;
}

.button {
    display: block;
    width: 30%;
}
</style>
