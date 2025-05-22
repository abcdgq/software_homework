<template>
  <div class="news-page">
    <div class="background-layer"></div>

    <!-- 左侧侧边栏 -->
    <div class="news-sidebar">
      <div class="filter-container">
        <!-- 来源筛选 -->
        <div class="filter-section">
          <h3 class="filter-title">来源筛选</h3>
          <el-select v-model="sourceFilter" placeholder="选择来源" size="small" class="source-select" style="width: 100%;">
            <el-option
              v-for="source in sources"
              :key="source"
              :label="source"
              :value="source === '全部' ? 'all' : source"
            />
          </el-select>
        </div>

        <!-- 时间筛选 -->
        <div class="filter-section">
          <h3 class="filter-title">时间范围</h3>
          <el-radio-group v-model="timeRange" class="vertical-radio-group">
            <el-radio label="all">全部</el-radio>
            <el-radio label="latest">三天内</el-radio>
            <el-radio label="week">五天内</el-radio>
            <el-radio label="month">一周内</el-radio>
          </el-radio-group>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="news-main-wrapper">
      <!-- 顶部搜索栏 -->
      <div class="news-header">
        <div class="search-container">
          <el-input
            v-model="searchQuery"
            placeholder="搜索资讯..."
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <el-button
              slot="append"
              icon="el-icon-search"
              @click="handleSearch"
            />
          </el-input>
        </div>
      </div>

      <div class="news-layout">
        <!-- 主内容区 -->
        <div class="news-main">
          <div v-if="!selectedNews" class="news-grid">
            <el-card
              v-for="(news, index) in filteredNews"
              :key="index"
              class="news-card"
              shadow="hover"
              style="cursor: pointer;"
            >
              <div @click="viewNewsDetail(news)">
                <div slot="header" class="clearfix">
                  <span class="news-title">{{ news.title }}</span>
                </div>
                <div class="news-content">
                  <p class="news-desc">
                    {{ news.summary.slice(0, 20) + (news.summary.length > 20 ? '...' : '') }}
                  </p>
                  <div class="news-footer">
                    <span class="news-source">{{ news.source }}</span>
                    <span class="news-time">{{ news.published }}</span>
                  </div>
                </div>
              </div>
            </el-card>
          </div>

          <!-- 新闻详情页 -->
          <div v-else class="news-detail">
            <el-button
              type="primary"
              icon="el-icon-arrow-left"
              @click="goBackToList"
              style="margin-bottom: 20px;"
            >
              返回
            </el-button>

            <el-card class="news-detail-card">
              <h2>{{ selectedNews.title }}</h2>
              <p class="news-authors" style="margin: 10px 0; font-weight: 500; color: #606266;">
                作者：{{ selectedNews.authors }}
              </p>
              <div style="margin: 10px 0;">
                <el-link
                  :href="selectedNews.link"
                  target="_blank"
                  type="primary"
                  icon="el-icon-link"
                  underline
                >
                  查看原文
                </el-link>
              </div>
              <p class="news-desc">{{ selectedNews.summary }}</p>
              <div class="news-footer">
                <span class="news-source">{{ selectedNews.source }}</span>
                <span class="news-time">{{ selectedNews.published }}</span>
              </div>
            </el-card>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      searchQuery: '',
      timeRange: 'all',
      sourceFilter: 'all',
      sources: [
        '全部',
        '人工智能',
        '机器学习',
        '计算机视觉与模式识别',
        '自然语言处理',
        '密码学与安全',
        '软件工程',
        '分布式与并行计算',
        '人机交互'
      ],
      newsList: [],
      selectedNews: null
    }
  },
  created () {
    this.fetchNews()
  },
  computed: {
    filteredNews () {
      return this.newsList.filter(news => {
        const matchesSearch =
          this.searchQuery === '' ||
          news.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          news.summary.toLowerCase().includes(this.searchQuery.toLowerCase())

        const matchesTime =
          this.timeRange === 'all' ||
          (this.timeRange === 'latest' && news.time === '三天内') ||
          (this.timeRange === 'week' && (news.time === '三天内' || news.time === '五天内')) ||
          (this.timeRange === 'month' && (news.time === '三天内' || news.time === '五天内' || news.time === '一周内'))

        const matchesSource =
          this.sourceFilter === 'all' || news.source === this.sourceFilter

        return matchesSearch && matchesTime && matchesSource
      })
    }
  },
  methods: {
    handleSearch () {},
    viewNewsDetail (news) {
      this.selectedNews = news
    },
    goBackToList () {
      this.selectedNews = null
    },
    fetchNews () {
      axios.get(this.$BASE_API_URL + '/news/fetchNews').then(response => {
        this.newsList = response.data.papers
      }).catch(error => {
        console.error('Error fetching news:', error)
      })
    }
  }
}
</script>

<style>
.background-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-image: url('../../assets/personal-back.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: -1;
}
</style>

<style scoped>
.news-page {
  position: relative;
  min-height: 100vh;
  padding-top: 60px;
  background-color: #f5f7fa; /* 若需要保底色 */
}

/* 搜索栏固定在右上 */
.news-header {
  position: fixed;
  top: 50px; /* 导航栏高度,但是60会滚动时候漏出字 */
  left: 250px;
  right: 0;
  z-index: 1000;
  background-color: rgba(255, 255, 255, 0.85); /* 半透明 */
  backdrop-filter: blur(8px); /* 毛玻璃模糊效果，增强可读性 */
  padding: 15px 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

/* 右下卡片内容可滚动 */
.news-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.search-input {
  width: 400px;
}

.news-layout {
  display: flex;
  max-width: 1200px;
  margin: 20px auto;
  gap: 20px;
}

.news-main-wrapper {
  margin-left: 250px;
  padding-top: 60px;  /* 给固定搜索栏留空间 */
  flex: 1;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px); /* 减去导航栏高度 */
  /* overflow: hidden; */
}

.news-main {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
  background-color: #f5f7fa; /* 和整体背景色保持一致 */
}

.news-sidebar {
  width: 250px;
  position: fixed;
  top: 50px; /* 导航栏高度，但是60会滚动时候漏出字 */
  bottom: 0;
  left: 0;
  overflow-y: auto;
  /* background-color: #fff; */
  background-color: transparent;
  padding: 20px;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  z-index: 999;
  /* 保持左侧栏布局 */
  display: flex;
  justify-content: center; /* 让内容横向居中 */
}

.filter-section {
  width: 100%;
  max-width: 160px;
  text-align: center;
  margin-bottom: 24px; /* 添加垂直间距 */
}

.vertical-radio-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 10px;
}

.vertical-radio-group .el-radio {
  margin: 8px 0;
}

.filter-title {
  color: #333;
  font-size: 16px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.filter-item {
  display: block;
  margin: 8px 0;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  cursor: pointer;
  margin-bottom: 5px;
}

.active-filters {
  background-color: #fff;
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.filter-label {
  color: #666;
  margin-right: 10px;
}

.active-filter-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.clear-all-btn {
  margin-left: 10px;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.news-card {
  transition: all 0.3s;
  border-radius: 8px;
}

.news-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

.news-title {
  font-weight: bold;
  font-size: 18px;
  margin-right: 10px;
}

.news-tag {
  margin-left: 5px;
}

.news-desc {
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}
.clearfix:after {
  clear: both
}

.news-detail {
  background-color: #fff;
  padding: 60px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.news-detail-card h2 {
  margin-bottom: 10px;
}

</style>
