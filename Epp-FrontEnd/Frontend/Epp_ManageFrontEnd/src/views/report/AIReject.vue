<template>
    <div class="report-manage-table">
        <!-- 搜索框 -->
        <div class="report-manage-search">
            <el-date-picker
                v-model="searchDate"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
            />
            <el-button type="primary" @click="handleSearch">搜索</el-button>
        </div>
        <!-- 表格内容 -->
        <el-table
            :data="aiReviewData.content"
            stripe
            style="width: 96%; border-top: 1px solid #edebeb; font-size: 15px; margin: 0 auto"
            size="large"
            v-loading="isLoading"
            :header-cell-style="{ 'text-align': 'center' }"
            :cell-style="{ 'text-align': 'center', 'vertical-align': 'middle' }"
            :default-sort="{ prop: 'date', order: 'descending' }"
        >
            <el-table-column label="序号" width="100" type="index"></el-table-column>
            <el-table-column label="日期" prop="date" width="200" sortable />
            <el-table-column label="用户" width="150">
                <template v-slot="scope">
                    <div class="table-text">
                        {{ scope.row.user.user_name }}
                    </div>
                </template>
            </el-table-column>
            <el-table-column label="被删除评论">
                <template v-slot="scope">
                    <div class="table-text">
                        {{ scope.row.comment.content }}
                    </div>
                </template>
            </el-table-column>
            <el-table-column label="删除原因">
                <template v-slot="scope">
                    <div class="table-text">
                        {{ scope.row.reason }}
                    </div>
                </template>
            </el-table-column>
            <el-table-column label="是否通过">
                <template v-slot="scope">
                    <div class="table-text">
                        {{ scope.row.isPassed }}
                    </div>
                </template>
            </el-table-column>
            <el-table-column type="expand">
                <template #default="props">
                    <a-i-review-detail :reviewID="props.row.id"></a-i-review-detail>
                </template>
            </el-table-column>
            <template v-slot:empty>
                <el-empty description="没有数据" />
            </template>
        </el-table>
        <!-- 分页组件 -->
        <el-pagination
            class="report-manage-pagination"
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 25, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="aiReviewData.total"
        />
    </div>
</template>

<script>
import { getAIReviewReject } from '@/api/aiReview'
import ReportDetail from './ReportDetail.vue'
import { ElMessage } from 'element-plus'
import AIReviewDetail from "@/views/report/AIReviewDetail.vue";
export default {
    components: {
        AIReviewDetail,
        ReportDetail
    },
    data() {
        return {
            isLoading: false,
            aiReviewData: {
                total: 2,
                content: [
                    {
                        id: 9,
                        comment: {
                            date: '2024-04-29 22:58:41',
                            content: '测试评论'
                        },
                        user: {
                            user_id: '063eccd4-76b3-4755-84c0-eef9baf16c04',
                            user_name: 'Ank'
                        },
                        date: '',
                        isPassed: '',
                        reason: '',
                    }
                ]
            },
            searchDate: '', // 搜索日期
            currentPage: 1, // 分页当前页
            pageSize: 10 // 分页大小
        }
    },
    methods: {
        async handleSearch() {
            this.isLoading = true
            await getAIReviewReject({
                date: this.searchDate,
                page_num: this.currentPage,
                page_size: this.pageSize
            })
                .then((response) => {
                    this.keywordBuffer = this.keyword
                    this.aiReviewData = {
                        total: response.data.total,
                        content: response.data.reports
                    }
                })
                .catch((error) => {
                    ElMessage.error(error.response.data.message)
                })
            this.isLoading = false
        }
    },
    created() {
        this.handleSearch() // 初始化列表
    }
}
</script>

<style lang="scss" scoped>
.report-manage-table {
    width: 100%;
    .report-manage-search {
        float: right;
        height: 8vh;
        line-height: 8vh;
        padding: 0 3%;
    }
    .report-manage-pagination {
        height: 10vh;
        margin-right: 2%;
        float: right;
    }
}

.table-text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
