<template>
    <el-container style="height: calc(100vh - 50px);">
        <el-header>
          <h3>调研助手</h3>
        </el-header>

        <el-main class="chat-content">
            <div v-for="(message, index) in chatMessages" :key="index">
                <div v-if="message.sender === 'ai'" class="message-bubble left">
                    <div v-if="message.loading" v-loading="message.loading"
                        element-loading-text="拼命加载中" element-loading-spinner="el-icon-loading" style="width: 100px; height: 40px;">
                    </div>
                    <div v-else>
                        <!-- <p style="white-space: pre-wrap;">{{ message.text }}</p> -->
                         <p style="white-space: pre-wrap;" v-html="renderMessageText(message)"></p>
                        <div v-if="message.type === 'query'" style="margin-top: 10px;">
                          <div v-for="(paper, index) of papers" :key="index">
                            <paper-card :paper="paper" />
                          </div>
                        </div>
                        <el-button v-show="message.type === 'query' && answerFinished && chatMessages.length - 1"
                        type="text" @click="searchPaperByAssistant">
                          <i class="fas fa-compass"></i>
                          论文循征
                        </el-button>
                    </div>
                </div>
                <div v-else class="message-bubble right">
                    <p style="word-wrap: break-word;">{{ message.text }}</p>
                </div>
            </div>
        </el-main>

        <el-footer>
          <el-input v-model="chatInput" :placeholder="isLoading ? '正在加载ai，请勿输入' : '输入你的消息...'"  @keyup.enter.native="chatToAI" clearable :disabled="isLoading"></el-input>
          <el-button type="primary" @click="chatToAI" :disabled="isLoading">发送</el-button>
        </el-footer>
    </el-container>
</template>

<script>
// import axios from 'axios'
import PaperCard from './PaperCard.vue'
export default {
  components: {
    'paper-card': PaperCard
  },
  props: {
    paperIds: {
      type: Array,
      default: null
    },
    searchRecordID: {
      type: String,
      default: ''
    },
    aiReply: {
      type: Array,
      default: null
    },
    restoreHistory: {
      type: Boolean,
      defrault: false
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      chatInput: '',
      chatMessages: [],
      answerFinished: false,
      papers: []
    }
  },
  created () {
    if (this.restoreHistory) {
      this.restoreDialogSearch()
    } else {
      this.createDialogStudy()
    }
  },
  mounted () {
    this.$el.addEventListener('click', e => {
      const target = e.target
      if (target.classList.contains('highlight-word')) {
        const word = target.dataset.word
        this.onWordClick(word)
      }
    })
  },
  methods: {
    createDialogStudy () {
      this.paperIds = this.paperIds.slice(0, 5)
      for (const message of this.aiReply) {
        this.chatMessages.push(message)
      }
    },
    async chatToAI () {
      const chatMessage = this.chatInput.trim()
      if (!chatMessage) {
        this.$message({
          message: '请输入你的问题',
          type: 'warning'
        })
        return
      }
      this.chatMessages.push({sender: 'user', text: chatMessage, loading: false, type: 'dialog'})
      let loadingMessage = { sender: 'ai', text: 'AI正在思考...', loading: true, type: 'dialog' }
      this.chatMessages.push(loadingMessage)
      let answer = ''
      this.chatInput = ''
      let highlights = []
      try {
        console.log('search-record-id: ', this.searchRecordID)
        await this.$axios.post(this.$BASE_API_URL + '/search/dialogQuery', { 'message': chatMessage, 'paper_ids': this.paperIds, 'search_record_id': this.searchRecordID })
          .then(response => {
            loadingMessage.type = response.data.dialog_type
            console.log(loadingMessage.type)
            if (loadingMessage.type === 'query') {
              this.papers = response.data.papers
            }
            loadingMessage.loading = false
            loadingMessage.text = ''
            answer = response.data.content
            highlights = response.data.highlights
            loadingMessage.highlights = highlights
          })
      } catch (error) {
        console.error('Error:', error)
        loadingMessage.text = ''
        answer = '抱歉, 无法从AI获取回应。'
        loadingMessage.loading = false
        loadingMessage.highlights = []
      } finally {
        this.answerFinished = false
        let cur = 0
        while (cur < answer.length) {
          loadingMessage.text += answer.charAt(cur)
          cur++
          await this.delay(50)
        }
        this.answerFinished = true
      }
    },
    createFakeData (loadingMessage) {
      loadingMessage.text = '以下为您找到几篇论文'
      loadingMessage.loading = false
      loadingMessage.type = 'query'
      this.answerFinished = true
      this.papers = [{
        'abstract': '  This document facilitates understanding of core concepts about uniform\nB-spline and its matrix representation.\n',
        'authors': 'Yi Zhou,',
        'citation_count': 39,
        'collect_count': 0,
        'comment_count': 0,
        'download_count': 635,
        'journal': null,
        'like_count': 0,
        'original_url': 'http://arxiv.org/abs/2309.15477v1',
        'paper_id': '04534e01-fea6-4676-adb0-3c9af9716dd2',
        'publication_date': 'Wed, 27 Sep 2023 00:00:00 GMT',
        'read_count': 516,
        'score': 0,
        'score_count': 0,
        'title': 'A Tutorial on Uniform B-Spline'
      }]
    },
    delay (ms) {
      return new Promise(resolve => setTimeout(resolve, ms))
    },
    // createKB () {
    //   console.log('创建知识库的论文ids', this.paperIds)
    //   let firstMessage = this.chatMessages[this.chatMessages.length - 1]
    //   firstMessage.loading = true
    //   axios.post(this.$BASE_API_URL + '/search/rebuildKB', {'paper_id_list': this.paperIds})
    //     .then((response) => {
    //       this.kbId = response.data.kb_id
    //       firstMessage.loading = false
    //       this.$message({
    //         message: '创建知识库成功',
    //         type: 'success'
    //       })
    //     })
    //     .catch((error) => {
    //       console.error('创建知识库失败', error)
    //       firstMessage.loading = false
    //       this.$message({
    //         message: '创建知识库失败',
    //         type: 'error'
    //       })
    //     })
    // },
    searchPaperByAssistant () {
      this.$emit('find-paper', this.papers)
    },
    restoreDialogSearch () {
      for (const message of this.aiReply) {
        this.chatMessages.push(message)
      }
    },
    renderMessageText (message) {
      if (!message.highlights || message.highlights.length === 0) {
        return message.text
      }

      const text = message.text
      const highlights = message.highlights.sort((a, b) => a.start - b.start)
      let result = ''
      let cur = 0

      highlights.forEach(hl => {
        if (cur < hl.start) {
          result += text.slice(cur, hl.start)
        }

        const word = text.slice(hl.start, hl.end)
        // 给特定词加上 span 和 data-* 属性
        result += `<span class="highlight-word" data-word="${word}" title="${hl.tooltip}">${word}</span>`
        cur = hl.end
      })

      if (cur < text.length) {
        result += text.slice(cur)
      }

      return result
    },
    async onWordClick (highlight) {
      console.log('Clicked word payload:')
      const chatMessage = '请具体解释其中的:' + highlight
      // this.chatInput = ''
      this.answerFinished = false
      this.chatMessages.push({sender: 'user', text: chatMessage, loading: false})

      let loadingMessage = { sender: 'ai', text: 'AI正在思考...', loading: true }
      this.chatMessages.push(loadingMessage)
      let answer = ''
      let highlights = []
      //   Add user message to chat
      try {
        await this.$axios.post(this.$BASE_API_URL + '/search/dialogQuery', { 'message': chatMessage, 'paper_ids': this.paperIds, 'search_record_id': this.searchRecordID })
          .then(response => {
            answer = response.data.ai_reply
            highlights = response.data.highlights
            loadingMessage.highlights = highlights
            this.docs = response.data.docs
            this.probQuestions = response.data.prob_question
            loadingMessage.loading = false
            loadingMessage.text = ''
          })
      } catch (error) {
        console.error('Error:', error)
        loadingMessage.text = ''
        answer = '抱歉, 无法从AI获取回应。'
        loadingMessage.loading = false
        loadingMessage.highlights = []
      } finally {
        this.answerFinished = false
        let cur = 0
        while (cur < answer.length) {
          loadingMessage.text += answer.charAt(cur)
          cur++
          await this.delay(50)
        }
        this.answerFinished = true
      }
    }
  }

}
</script>

<style scoped>
.el-header {
  text-align: center;
  padding: 20px;
}

.chat-content {
  display: flex;
  flex-direction: column;
  align-items: stretch; /* 确保元素可以根据需要对齐到左边或右边 */
  background: rgb(233, 242, 251);
  width: 100%; /* 可以调整宽度以适应不同屏幕大小 */
}

.el-footer {
  background: rgb(233, 242, 251);
  display: flex;
  align-items: center;
  height: 100%;
  margin: 0;
}

.message-bubble {
  position: relative;
  display: inline-block;
  padding: 10px 20px;
  border: 1px solid #ccc;
  margin: 5px 0;
  overflow-y: auto;
  text-align: left;
}

.message-bubble p {
    margin: 0;
}

.right {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
  float: right;
  border-radius: 15px 0 15px 15px;
  clear: both;
  word-break: break-all;
}

.left {
  background-color: white;
  color: black;
  border-color: #ccc;
  float: left;
  clear: both;
  border-radius: 0 15px 15px 15px;
}

/deep/ .highlight-word {
  text-decoration: underline wavy #1e90ff; /* 使用常见的蓝色 (DodgerBlue) */
  text-underline-offset: 2px;              /* 微调下划线的位置 */
  /* text-decoration-thickness: 2px;             加粗下划线 */
  cursor: pointer;
}
</style>
