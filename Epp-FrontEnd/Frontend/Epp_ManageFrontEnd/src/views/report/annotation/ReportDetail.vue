<template>
    <div style="padding: 5px">
        <div class="report-card">
            <el-card class="report-content" shadow="hover">
                <div>
                    <el-descriptions title="批注信息" colum="1" border>
                        <el-descriptions-item label="批注用户">
                            {{ reportDetail.annotation.user }}
                        </el-descriptions-item>
                        <el-descriptions-item label="批注时间">
                            {{ reportDetail.annotation.date }}
                        </el-descriptions-item>
                        <el-descriptions-item label="批注内容">
                            {{ reportDetail.annotation.note.comment }}
                        </el-descriptions-item>
                    </el-descriptions>
                    <el-divider />

                    <el-descriptions title="批注论文" column="1" border>
                        <el-descriptions-item label="论文标题">
                            {{ reportDetail.paper }}
                        </el-descriptions-item>
                    </el-descriptions>
                    <el-divider />

                    <el-descriptions title="举报信息" column="1" border>
                        <el-descriptions-item label="举报用户">
                            {{ reportDetail.user }}
                        </el-descriptions-item>
                        <el-descriptions-item label="举报日期">
                            {{ reportDetail.date }}
                        </el-descriptions-item>
                        <el-descriptions-item label="举报内容">
                            {{ reportDetail.content }}
                        </el-descriptions-item>
                    </el-descriptions>
                </div>
            </el-card>

            <div class="report-judge">
                <div class="report-judge-header">举报审核</div>
                <div style="padding: 16px">
                    <el-input
                        v-model="judgment.text"
                        sytle="width: 100%; min-height: 50%"
                        :autosize="{ minRows: 10, maxRows: 20 }"
                        type="textarea"
                        placeholder="请输入审核意见"
                        maxlength="200"
                        show-word-limit
                        />
                    <div style="margin-top: 20px">
                        <span>删除批注</span>
                        <el-switch
                            v-model="judgment.invisibility"
                            style="margin-left: 10px; --el-switch-on-color: #13ce66; --el-switch-off-color: #d0d0d0"
                            />
                    </div>

                    <div style="margin-top: 20px">
                        <el-button
                            v-if="reportDetail.processed"
                            class="button"
                            type="primary"
                            round
                            style="margin: 0 auto"
                            @click="handleSubmit"
                            >确认修改</el-button>
                        <el-button
                            v-else
                            class="button"
                            type="primary"
                            round
                            style="margin:0 auto"
                            >确认提交</el-button>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<script>
import {getAnnotReportDetail} from '@/api/report.js'
import {judgeAnnotReport} from "@/api/report.js"

export default {
    props: { reportID: Number },
    data() {
        return {
            reportDetail: {
                annotation: {
                    annotation_id: 1,
                    user: '批注用户',
                    paper: '对应论文',
                    date: '',
                    note: {
                        note_id: 1,
                        x: 0.5,
                        y: 0.6,
                        width: 20,
                        height: 10,
                        pageNum: 10,
                        comment: '',
                        username: '',
                        isPublic: true
                    }
                },

                user: '举报用户',
                date: '',
                content: '低俗，色情',
                judgment: '审核意见',
                acceptReport: true,
                processed: false
            },

            judgment: {
                text: '审核意见',
                invisibility: true
            }
        }
    },

    methods: {
        async draw() {
            await getAnnotReportDetail(this.$props.reportID)
                .then((response) => {
                    this.reportDetail = response.data
                    this.judgment.text = response.data.judgment
                    this.judgment.invisibility = response.data.acceptReport
                })
                .catch((error) => {
                    console.log(this.$props.reportID)
                    console.log(error)
                })
        },

        async handleSubmit() {
            await judgeAnnotReport({
                reportID: this.$props.reportID,
                text: this.judgment.text,
                visibility: !this.judgment.invisibility
            })
                .then((response) => {
                    console.log(response.data.message)
                })
                .catch((error) => {
                    console.log(error.response.data.message)
                })
        }
    },
    watch: {
        reportID: {
            handler() {
                this.draw()
            },
            immediate: true
        }
    },

}
</script>


<style>
.report-card {
    display: flex;
    flex-direction: row;
    justify-content: center;
    .report-content {
        width: 60%;
        padding: 20px;
        border: 0px !important;
        border-right: 1px solid #dbdbdb !important;
        border-radius: 0px !important;
        background-color: #fff;
    }

    .report-judge {
        width: 40%;
        padding: 20px;
        .report-judge-header {
            margin-top: 20px;
            color: #303133;
            font-weight: bold;
        }
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