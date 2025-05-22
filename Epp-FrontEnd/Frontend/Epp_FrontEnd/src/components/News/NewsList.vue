<template>
  <div class="news-page">
    <div class="background-layer"></div>
    <!-- 左侧筛选区 -->
      <div class="news-sidebar">
        <div class="filter-section">
          <h3 class="filter-title">资讯分类</h3>
          <el-checkbox-group v-model="selectedCategories">
            <el-checkbox
              v-for="category in categories"
              :key="category"
              :label="category"
              class="filter-item"
            >
              {{ category }}
            </el-checkbox>
          </el-checkbox-group>
        </div>

        <div class="filter-section">
          <h3 class="filter-title">热门标签</h3>
          <div class="tag-cloud">
            <el-tag
              v-for="tag in popularTags"
              :key="tag"
              :type="selectedTags.includes(tag) ? 'primary' : 'info'"
              class="tag-item"
              @click="toggleTag(tag)"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>

        <div class="filter-section">
          <h3 class="filter-title">时间范围</h3>
          <el-radio-group v-model="timeRange">
            <el-radio label="all">全部</el-radio>
            <el-radio label="today">今天</el-radio>
            <el-radio label="week">本周</el-radio>
            <el-radio label="month">本月</el-radio>
          </el-radio-group>
        </div>
      </div>

    <!-- 右侧区域 -->
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
            <!-- 资讯列表或详情 -->
            <div class="news-main">
            <!-- 筛选标签区域只在列表视图中显示 -->
                <div v-if="!selectedNews && activeFilters.length > 0" class="active-filters">
                    <span class="filter-label">当前筛选：</span>
                    <el-tag
                    v-for="filter in activeFilters"
                    :key="filter"
                    closable
                    @close="removeFilter(filter)"
                    class="active-filter-tag"
                    >
                    {{ filter }}
                    </el-tag>
                    <el-button
                    type="text"
                    @click="clearAllFilters"
                    class="clear-all-btn"
                    >
                    清除所有
                    </el-button>
                </div>

                <!-- 列表视图 -->
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
                                <el-tag
                                    v-for="tag in news.tags"
                                    :key="tag"
                                    size="mini"
                                    type="info"
                                    class="news-tag"
                                >
                                    {{ tag }}
                                </el-tag>
                            </div>
                            <div class="news-content">
                                <p class="news-desc">{{ news.description }}</p>
                                <div class="news-footer">
                                    <span class="news-source">{{ news.source }}</span>
                                    <span class="news-time">{{ news.time }}</span>
                                </div>
                            </div>
                        </div>
                    </el-card>
                </div>

                <!-- 详情视图 -->
                <div v-else class="news-detail">
                    <el-button type="primary" icon="el-icon-arrow-left" @click="goBackToList" style="margin-bottom: 20px;">
                    返回
                    </el-button>
                    <el-card class="news-detail-card">
                    <h2>{{ selectedNews.title }}</h2>
                    <div style="margin: 10px 0;">
                        <el-tag
                        v-for="tag in selectedNews.tags"
                        :key="tag"
                        size="mini"
                        type="info"
                        style="margin-right: 5px;"
                        >
                        {{ tag }}
                        </el-tag>
                    </div>
                    <p class="news-desc">{{ selectedNews.description }}</p>
                    <div class="news-footer">
                        <span class="news-source">{{ selectedNews.source }}</span>
                        <span class="news-time">{{ selectedNews.time }}</span>
                    </div>
                    </el-card>
                </div>
            </div>
        </div>
    </div>

  </div>
</template>

<script>
export default {
  data () {
    return {
      searchQuery: '',
      selectedCategories: [],
      selectedTags: [],
      timeRange: 'all',
      categories: ['科技', '前端', '人工智能', 'Web开发', 'TypeScript'],
      popularTags: ['Vue', 'React', 'JavaScript', 'CSS', 'Node.js', '工程化', '性能优化'],
      newsList: [
        {
          title: 'Vue 3.4 正式发布，性能大幅提升',
          description: 'Vue 3.4 版本带来了多项性能优化和新特性，包括更快的渲染速度和改进的响应式系统...',
          source: '前端周刊',
          time: '3小时前',
          category: '前端',
          tags: ['Vue', 'JavaScript', '性能优化']
        },
        {
          title: '人工智能助力前端开发',
          description: '最新研究表明，AI代码助手可以提升前端开发效率达40%，Vue和React开发者受益明显...',
          source: '科技前沿',
          time: '1天前',
          category: '人工智能',
          tags: ['AI', '前端', '开发工具']
        },
        {
          title: 'Element Plus 2.4 版本发布',
          description: '基于Vue 3的Element Plus组件库迎来重大更新，新增多个实用组件和功能...',
          source: 'UI框架日报',
          time: '2天前',
          category: '前端',
          tags: ['Vue', 'UI', 'Element']
        },
        {
          title: 'WebAssembly 应用场景扩展',
          description: 'WebAssembly不仅限于游戏和图形处理，现在已广泛应用于音视频处理、加密计算等领域...',
          source: '开发者日报',
          time: '3天前',
          category: 'Web开发',
          tags: ['WebAssembly', '性能优化']
        },
        {
          title: 'TypeScript 5.0 新特性解析',
          description: 'TypeScript 5.0 引入了装饰器新标准、性能优化和多项语法改进，提升开发体验...',
          source: 'TypeScript社区',
          time: '4天前',
          category: '前端',
          tags: ['TypeScript', 'JavaScript']
        },
        {
          title: '前端工程化最佳实践',
          description: '2024年前端工程化最新趋势：模块联邦、微前端架构和自动化测试成为标配...',
          source: '工程化月刊',
          time: '5天前',
          category: '前端',
          tags: ['工程化', 'Webpack', '微前端']
        },
        {
          title: 'TypeScript 5.0 新特性解析',
          description: 'TypeScript 5.0 引入了装饰器新标准、性能优化和多项语法改进，提升开发体验...',
          source: 'TypeScript社区',
          time: '4天前',
          category: '前端',
          tags: ['TypeScript', 'JavaScript']
        },
        {
          title: 'TypeScript 5.0 新特性解析',
          description: 'TypeScript 5.0 引入了装饰器新标准、性能优化和多项语法改进，提升开发体验...',
          source: 'TypeScript社区',
          time: '4天前',
          category: '前端',
          tags: ['TypeScript', 'JavaScript']
        },
        {
          title: 'TypeScript 5.0 新特性解析',
          description: 'TypeScript 5.0 引入了装饰器新标准、性能优化和多项语法改进，提升开发体验...',
          source: 'TypeScript社区',
          time: '4天前',
          category: '前端',
          tags: ['TypeScript', 'JavaScript']
        },
        {
          title: 'TypeScript 5.0 新特性解析',
          description: 'TypeScript 5.0 引入了装饰器新标准、性能优化和多项语法改进，提升开发体验...',
          source: 'TypeScript社区',
          time: '4天前',
          category: '前端',
          tags: ['TypeScript', 'JavaScript']
        },
        {
          title: 'TypeScript 5.0 新特性解析',
          description: 'TypeScript 5.0 引入了装饰器新标准、性能优化和多项语法改进，提升开发体验...',
          source: 'TypeScript社区',
          time: '4天前',
          category: '前端',
          tags: ['TypeScript', 'JavaScript']
        },
        {
          title: 'TypeScript 5.0 新特性解析',
          description: 'TypeScript 5.0 引入了装饰器新标准、性能优化和多项语法改进，提升开发体验...',
          source: 'TypeScript社区',
          time: '4天前',
          category: '前端',
          tags: ['TypeScript', 'JavaScript']
        }
      ],
      selectedNews: null // 新增：当前选中的资讯详情
    }
  },
  computed: {
    filteredNews () {
      return this.newsList.filter(news => {
        // 搜索查询匹配
        const matchesSearch = this.searchQuery === '' ||
          news.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          news.description.toLowerCase().includes(this.searchQuery.toLowerCase())
        // 分类匹配
        const matchesCategory = this.selectedCategories.length === 0 ||
          this.selectedCategories.includes(news.category)
        // 标签匹配
        const matchesTags = this.selectedTags.length === 0 ||
          this.selectedTags.some(tag => news.tags.includes(tag))
        // 时间范围匹配 (简化处理)
        const matchesTime = this.timeRange === 'all' ||
          (this.timeRange === 'today' && news.time.includes('小时')) ||
          (this.timeRange === 'week' && !news.time.includes('月')) ||
          (this.timeRange === 'month' && true) // 示例逻辑
        return matchesSearch && matchesCategory && matchesTags && matchesTime
      })
    },
    activeFilters () {
      return [
        ...this.selectedCategories,
        ...this.selectedTags,
        this.timeRange !== 'all' ? `时间: ${this.timeRange}` : ''
      ].filter(Boolean)
    }
  },
  methods: {
    handleSearch () {
      // 搜索逻辑已在计算属性中处理
    },
    toggleTag (tag) {
      if (this.selectedTags.includes(tag)) {
        this.selectedTags = this.selectedTags.filter(t => t !== tag)
      } else {
        this.selectedTags.push(tag)
      }
    },
    removeFilter (filter) {
      if (this.selectedCategories.includes(filter)) {
        this.selectedCategories = this.selectedCategories.filter(c => c !== filter)
      } else if (this.selectedTags.includes(filter)) {
        this.selectedTags = this.selectedTags.filter(t => t !== filter)
      } else if (filter.startsWith('时间:')) {
        this.timeRange = 'all'
      }
    },
    clearAllFilters () {
      this.searchQuery = ''
      this.selectedCategories = []
      this.selectedTags = []
      this.timeRange = 'all'
    },
    viewNewsDetail (news) {
      this.selectedNews = news
      // TODO 这里添加查看资讯详情的逻辑，可以向后端获取具体资讯内容。
    //   alert(`查看资讯详情: ${news.title}`)
    },
    goBackToList () {
      this.selectedNews = null
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

.filter-section {
  margin-bottom: 25px;
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
