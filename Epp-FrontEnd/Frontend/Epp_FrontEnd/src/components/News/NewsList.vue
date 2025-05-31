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
              :key="source.value"
              :label="source.label"
              :value="source.value"
            />
          </el-select>
        </div>

        <!-- 时间筛选 -->
        <div class="filter-section">
          <h3 class="filter-title">时间范围</h3>
          <el-radio-group v-model="timeRange" class="vertical-radio-group">
            <el-radio label="all">全部</el-radio>
            <el-radio label="latest">一天内</el-radio>
            <el-radio label="threeDays">三天内</el-radio>
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
        <div class="summary-panel">
          <!-- <h3 class="summary-title">资讯总结</h3> -->
          <el-button type="primary" size="small" @click="fetchSummary">获取资讯总结</el-button>
          <div class="summary-content" v-html="summaryText"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import MarkdownIt from 'markdown-it' // 引入markdown-it

export default {
  data () {
    return {
      md: null, // 存储markdown-it实例
      searchQuery: '',
      timeRange: 'all',
      sourceFilter: 'all',
      sources: [
        { label: '全部', value: 'all' },
        { label: '人工智能', value: 'AI' },
        { label: '机器学习', value: 'ML' },
        { label: '计算机视觉与模式识别', value: 'CV' },
        { label: '自然语言处理', value: 'NLP' },
        { label: '密码学与安全', value: 'CR' },
        { label: '软件工程', value: 'SE' },
        { label: '分布式与并行计算', value: 'DC' },
        { label: '人机交互', value: 'HC' }
      ],
      // newsList: [],
      newsList: [
        // {
        //   title: '示例新闻标题',
        //   summary: '这是一个示例新闻摘要，用于展示新闻列表的样式。',
        //   source: '人工智能',
        //   published: '2023-10-01',
        //   link: 'https://example.com/news1',
        //   authors: '张三, 李四',
        //   time: '三天内'
        // }
      ],
      selectedNews: null,
      summaryText: ''
    }
  },
  created () {
    this.fetchNews()
    this.md = new MarkdownIt() // 初始化markdown-it实例
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
          (this.timeRange === 'latest' && news.time === '一天内') ||
          (this.timeRange === 'threeDays' && (news.time === '一天内' || news.time === '三天内'))
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
      this.$message({
        message: '正在更新新闻数据，请稍候...',
        type: 'warning'
      })
      axios.get(this.$BASE_API_URL + '/news/fetchNews').then(response => {
        this.newsList = response.data.papers
        console.log('新闻数据已更新:', this.newsList)
        this.$message({
          message: '新闻数据已更新',
          type: 'success'
        })
      }).catch(error => {
        console.error('Error fetching news:', error)
      })
    },
    fetchSummary () {
      this.$message({
        message: '正在获取总结，请稍候...',
        type: 'info'
      })
      axios.get(this.$BASE_API_URL + '/news/getSummary')
        .then(response => {
          this.summaryText = this.md.render(response.data.summary)
          console.log('总结加载成功:', response.data.summary)
          this.$message({
            message: '总结加载成功',
            type: 'success'
          })
        })
        .catch(error => {
          // this.summaryText = '<p>获取失败，请稍后再试。</p>'
          this.summaryText = `
  <div class="markdown-body">
    <div class="error-message">
      <h3 style="color: #f56c6c;">获取总结失败</h3>
      <p>抱歉，暂时无法加载内容。请稍后再试或联系管理员。</p>
      <div class="error-details" style="margin-top: 16px; padding: 12px; background-color: #f8f8f8; border-radius: 4px;">
        <p style="font-size: 14px; color: #606266;">错误信息：</p>
        <pre style="margin: 8px 0; padding: 8px; background-color: #f0f2f5; border-radius: 4px; font-family: monospace; font-size: 13px;">${'网络不佳'}</pre>
      </div>
    </div>
  </div>
`
          console.error('获取总结失败:', error)
          this.$message.error('获取总结失败')
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
  margin: 0 auto;
  gap: 20px;
  height: calc(100vh - 120px); /* 保证撑满视口高度，考虑 header 和 margin */
}

.news-main-wrapper {
  margin-left: 250px;
  padding-top: 60px;  /* 给固定搜索栏留空间 */
  /* flex: 1; */
  display: flex;
  /* flex-direction: column; */
  /* height: calc(100vh - 60px); 减去导航栏高度 */
  /* overflow: hidden; */
}

.news-main {
  width: 900px;
  height: 100%;
  overflow-y: auto;
  padding-right: 10px;
  background-color: #f5f7fa;
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
  grid-template-columns: repeat(2, 1fr);
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

.summary-panel {
  width: 100%; /* 占满父容器宽度 */
  max-width: 360px; /* 保留最大宽度限制 */
  flex-shrink: 0;
  background-color: #fff;
  padding: 0; /* 移除内边距，让内容直接填充 */
  border-radius: 8px;
  height: 100%;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding-top: 24px;
  /* 移除 overflow-y: auto，让内容自己处理滚动 */
}

.summary-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}

.summary-content {
  margin-top: 15px;
  max-height: calc(100% - 70px);
  overflow-y: auto;
  line-height: 1.6;
  color: #333;
  padding: 16px 24px; /* 增加左右内边距至 24px */
  border-radius: 8px;
  background-color: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.summary-content .error-message:before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 4px;
  background-color: #f56c6c;
}

.summary-content .error-message h3 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #f56c6c;
  font-size: 1.2em;
  display: flex;
}

.summary-content .error-message h3::before {
  content: '⚠️';
  margin-right: 8px;
  font-size: 1.1em;
}

.summary-content .error-message p {
  margin: 0.8em 0;
  color: #606266;
}

/* 错误详情区域优化 */
.summary-content .error-details {
  margin-top: 16px;
  padding: 16px;
  background-color: #ffffff;
  border-radius: 6px;
  border: 1px solid #ebeef5;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.summary-content .error-details p {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

.summary-content .error-details pre {
  margin: 0;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
  color: #333;
  white-space: pre-wrap;
  word-break: break-all;
}

/* Markdown内容样式 */
.summary-content h1,
.summary-content h2,
.summary-content h3 {
  margin: 1em 0 0.5em;
  font-weight: bold;
}

.summary-content h1 { font-size: 1.5em; }
.summary-content h2 { font-size: 1.3em; }
.summary-content h3 { font-size: 1.1em; }

.summary-content ul,
.summary-content ol {
  margin: 0.8em 0;
  padding-left: 2em;
  text-align: left; /* 确保列表居左 */
}

.summary-content code {
  font-family: monospace;
  background-color: #f5f5f5;
  padding: 0.2em 0.4em;
  border-radius: 3px;
}

.summary-content pre code {
  background-color: transparent;
  padding: 0;
}

</style>

<style>
.summary-content p {
  margin: 0.8em 0;
  text-align: left !important; /* 确保段落居左 */
}

/* 错误消息样式优化 */
.summary-content .error-message {
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #fde2e2;
  background-color: #fef6f6;
  position: relative;
  overflow: hidden;
  text-align: left !important; /* 确保内容居左 */
}
.summary-content pre {
  background-color: #f5f5f5;
  padding: 1em;
  border-radius: 4px;
  overflow: auto;
  text-align: left !important; /* 确保代码块居左 */

}
.summary-content blockquote {
  margin: 1em 0;
  padding: 0.5em 1em;
  background-color: #f8f8f8;
  border-left: 4px solid #ddd;
  color: #666;
  text-align: left !important; /* 确保引用居左 */
}

#app .summary-content li {
  text-align: left !important;
}

</style>
