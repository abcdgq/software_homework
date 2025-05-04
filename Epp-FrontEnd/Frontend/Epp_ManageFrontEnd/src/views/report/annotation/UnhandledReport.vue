<template>
    <div class="report-manage-table">
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

        <el-table
            :data='reportData.reports'
            stripe
            style="width: 96%; border-top: 1px solid #edebeb; font-size: 15px; margin: 0 auto"
            size="large"
            v-loading="isLoading"
            :header-cell-style="{ 'text-align': 'center' }"
            :cell-style="{ 'text-align': 'center', 'vertical-align': 'center' }"
            :default-sort="{ prop: 'date', order: 'descending' }"
            >
            <el-table-column label="序号" width="100" type="index" />
            <el-table-column label="日期" prop="date" width="200" sortable />
            <el-table-column label="用户" width="150">
                <template v-slot="scope">
                    <div class="table-text">
                        {{ scope.row.user.user_name }}
                    </div>
                </template>
            </el-table-column>

            <el-table-column label="被举报批注">
                <template v-slot="scope">
                    <div class="table-text">
                        {{ scope.row.annotation.content}}
                    </div>
                </template>
            </el-table-column>
            <el-table-column label="举报理由">
                <template v-slot="scope">
                    <div class="table-text">
                        {{ scope.row.content }}
                    </div>
                </template>
            </el-table-column>
            <el-table-column type="expand">
                <template #default="props">
                    <report-detail :reportID="props.row.report_id" />
                </template>
            </el-table-column>
            <template #empty>
                <el-empty description="没有数据" />
            </template>
        </el-table>

        <el-pagination
            class="report-manage-pagination"
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 25, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="reportData.total"
            />
    </div>
</template>

<script>
import ReportDetail from '@/views/report/annotation/ReportDetail.vue'
import {getAnnotReportUnhandled} from '@/api/report.js'

export default {
    components: {
        ReportDetail
    },
    data() {
        return {
            isLoading: false,
            reportData: {
                total: 1,
                reports: [
                    {
                        report_id: 1,
                        annotation: {
                            date: '2025-05-01 10:28:28',
                            content: '批注内容'
                        },
                        user: {
                            user_id: '22370000',
                            user_name: '张三'
                        },
                        date: '2025-05-01 10:28:28',
                        content: '色情，暴力'
                    }
                ]
            },
            searchDate: '',
            currentPage: 1,
            pageSize: 10
        }
    },

    methods: {
        async handleSearch() {
            this.isLoading = true
            await getAnnotReportUnhandled({
                date: this.searchDate,
                pageNum: this.currentPage,
                pageSize: this.pageSize
            })
                .then((response) => {
                    console.log('getAnnotReportUnhandled:\n', response)
                    this.reportData = response.data
                    console.log(response.data.reports[0].report_id)
                    console.log(this.reportData.reports[0].report_id)
                })
                .catch((error) => {
                    console.log(error.response.data.message)
                })
            this.isLoading = false
        }
    },
    created() {
        this.handleSearch()
    }
}
</script>

<style>
.report-manage-table {
    width: 100%;

    .table-text {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis
    }
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
</style>
