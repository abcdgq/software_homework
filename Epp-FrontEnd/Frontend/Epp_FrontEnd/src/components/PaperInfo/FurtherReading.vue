<template>
    <el-card shadow="always" class="further-reading">
        <div class="header">
            <span><el-icon>  </el-icon>延伸阅读</span>
            <el-button icon="el-icon-arrow-down" @click="toggleCollapse"/>
        </div>

        <el-collapse-transition>
            <div v-show="!collapsed">
                <el-empty v-if="papers.length === 0 && !loading" description="暂无推荐文献"/>
                <div v-else>
                    <div
                        v-for="(paper, index) in papers"
                        :key="index"
                        class="paper-card"
                    >
                        <div class="title"> {{ paper.title }}</div>
                        <div class="summary"> {{ paper.summary }}</div>

                        <el-row class="card-actions">
                            <router-link
                                :to="{ name: 'paper-info', params: { paper_id: paper.id } }"
                                style="margin-right: 12px;"
                                >
                                <el-button
                                    type="text"
                                    icon="el-icon-document"
                                >查看论文</el-button>
                            </router-link>

                            <el-button
                                type="text"
                                :icon="paper.collected? 'el-icon-star-on' : 'el-icon-star-off'"
                                @click="toggleCollected(index)"
                            >收藏</el-button>
                        </el-row>
                    </div>
                </div>
            </div>
        </el-collapse-transition>
    </el-card>
</template>
<script>
import {collectPaper, fetchFurtherReadingPapers} from '../../api/Paper'

export default {
    props: {
        paperId: String
    },
    data() {
        return {
            loading: false,
            collapsed: false,
            papers: [
                {
                    id: '',
                    title: 'This is the title of the paper',
                    summary: '一句话推荐',
                    collected: false // 该论文是否已经添加到收藏
                },
                {
                    id: '',
                    title: 'This is the title of the paper',
                    summary: '一句话推荐',
                    collected: false // 该论文是否已经添加到收藏
                }
            ],
        }
    },

    methods: {
        toggleCollapse() {
            this.collapsed = !this.collapsed
        },
        async toggleCollected(index) {
            await collectPaper(this.papers[index].id)
                .then((response) => {
                    this.papers[index].collected = !this.papers[index].collected
                })
                .catch((error) => {
                    console.log(error.response.data.message)
                })
        },

        async fetchPapers() {
            this.loading = true
            await fetchFurtherReadingPapers(this.paperId)
                .then((response) => {
                    this.papers = response.data
                })
                .catch((error) => {
                    console.log(error)
                })
            this.loading = false
        },
    },
    created() {
        this.fetchPapers()
    }
}
</script>

<style scoped>
.further-reading {
    max-width: 100%;
    max-height: 200%;
    margin: 0 auto;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
    margin-bottom: 12px;
}

.paper-card {
    margin-bottom: 12px;
    padding: 10px;
}

.title {
    font-weight: 600;
    font-size: 15px;
    margin-bottom: 4px;
}

.summary {
    font-size: 14px;
    margin-bottom: 6px;
    color: #666;
}

.card-actions {
    display: flex;
    align-items: center;
}
</style>