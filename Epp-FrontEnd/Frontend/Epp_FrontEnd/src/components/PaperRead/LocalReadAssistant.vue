<template>

  <el-container style="height: calc(100vh - 110px);" class="read-assistant">
    <el-header class="my-header">
      <h3>调研助手</h3>
      <div>
        <el-tooltip class="item" effect="dark" content="一键总结" placement="top">
          <el-button type="success" plain size="small" @click="renderMarkdown()" icon="fas fa-file-text"></el-button>
        </el-tooltip>
        <el-tooltip class="item" effect="dark" content="清除历史对话" placement="top">
          <el-button type="primary" plain size="small" @click="clearHistory()" icon="fas fa-eraser"
            style="margin-right: 10px;"></el-button>
        </el-tooltip>
        <el-dialog :visible.sync="showSummaryModal" width="70%">
            <div v-html="markdownFile" style=""></div>
        </el-dialog>
      </div>
    </el-header>

    <el-main class="chat-content">
      <div v-for="(message, index) in chatMessages" :key="index">
        <div v-if="message.sender === 'ai'" class="message-bubble left">
          <div v-if="message.loading" v-loading="message.loading" element-loading-text="拼命加载中"
            element-loading-spinner="el-icon-loading" style="width: 100px; height: 40px;">
          </div>
          <div v-else>
            <!-- <p style="white-space: pre-wrap;">{{ message.text }}</p> -->
            <p style="white-space: pre-wrap;" v-html="renderMessageText(message)"></p>
            <el-button type="text" @click="regenerateAnswer"
              v-show="index == chatMessages.length - 1 && answerFinished">
              <i class="fas fa-refresh"></i>
              重新生成
            </el-button>
            <el-button type="text" @click="findReplySource" v-show="index == chatMessages.length - 1 && answerFinished">
              <i class="fas fa-quote-right"></i>
              查询出处
            </el-button>
          </div>
        </div>
        <div v-else class="message-bubble right">
          <p style="white-space: pre-wrap;">{{ message.text }}</p>
        </div>
      </div>
      <div style="margin-top: 10px;">
        <div v-show="answerFinished" v-for="(question, index) in probQuestions" :key="index" class="prob-question"
          @click="sendProbQuestion(question)">
          {{ question }}
        </div>
      </div>
    </el-main>

    <el-footer>
      <el-input v-model="chatInput" placeholder="输入你的消息..." @keyup.enter.native="chatToAI"></el-input>
      <el-button type="primary" @click="chatToAI">发送</el-button>
    </el-footer>
  </el-container>
</template>

<script>
import axios from 'axios'
// import markdownIt from 'markdown-it'
export default {
  props: {
    paperID: {
      type: String,
      default: ''
    },
    fileReadingId: {
      type: String,
      default: ''
    }
  },
  data () {
    return {
      chatInput: '',
      chatMessages: [],
      answerFinished: false,
      probQuestions: [],
      showSummaryModal: false,
      markdownFile: '',
      fileReadingID: ''
    }
  },
  mounted () {
    this.fileReadingID = this.fileReadingId
    this.initialize()
    this.$el.addEventListener('click', e => {
      const target = e.target
      if (target.classList.contains('highlight-word')) {
        const word = target.dataset.word
        this.onWordClick(word)
      }
    })
  },
  methods: {
    initialize () {
      if (this.fileReadingID) {
        this.restorePaperStudy()
      } else {
        this.createPaperStudy()
      }
    },
    async createPaperStudy () {
      const loadingInstance = this.$loading({
        lock: true,
        text: '正在初始化...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)',
        target: '.read-assistant'
      })
      await axios.post(this.$BASE_API_URL + '/study/createPaperStudy', {'document_id': this.paperID, 'file_type': 1})
        .then((response) => {
          if (response.status === 200) {
            this.fileReadingID = response.data.file_reading_id
            if (response.data.conversation_history.conversation.length > 0) {
              const history = response.data.conversation_history.conversation
              for (const message of history) {
                const sender = message.role === 'user' ? 'user' : 'ai'
                this.chatMessages.push({sender: sender, text: message.content, loading: false})
              }
              this.$message({
                message: '已恢复研读对话',
                type: 'success'
              })
              loadingInstance.close()
            } else {
              this.$message({
                message: '论文研读知识库创建成功！',
                type: 'success'
              })
              loadingInstance.close()
            }
          }
        })
        .catch(() => {
          this.$message({
            message: '无法获取论文研读知识库！',
            type: 'success'
          })
          loadingInstance.close()
        })
        .finally(() => {
          loadingInstance.close()
        })
    },
    async restorePaperStudy () {
      console.log('研读对话的id, ', this.fileReadingID)
      const loadingInstance = this.$loading({
        lock: true,
        text: '正在恢复知识库...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)',
        target: '.read-assistant' // 指定加载动画的目标
      })
      await axios.post(this.$BASE_API_URL + '/study/restorePaperStudy', {'file_reading_id': this.fileReadingID})
        .then((response) => {
          const history = response.data.conversation_history.conversation
          for (const message of history) {
            const sender = message.role === 'user' ? 'user' : 'ai'
            this.chatMessages.push({sender: sender, text: message.content, loading: false})
          }
          this.$message({
            message: '已恢复研读对话',
            type: 'success'
          })
          loadingInstance.close()
        })
        .catch((error) => {
          console.error('恢复论文研读失败: ', error)
          this.$message({
            message: '恢复论文研读失败！',
            type: 'success'
          })
          loadingInstance.close()
        })
        .finally(() => {
          loadingInstance.close()
        })
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
      this.chatInput = ''
      this.answerFinished = false
      this.chatMessages.push({sender: 'user', text: chatMessage, loading: false})

      let loadingMessage = { sender: 'ai', text: 'AI正在思考...', loading: true }
      this.chatMessages.push(loadingMessage)
      let answer = ''
      let highlights = []
      //   Add user message to chat
      try {
        await this.$axios.post(this.$BASE_API_URL + '/study/doPaperStudy', { 'query': chatMessage, 'file_reading_id': this.fileReadingID })
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
        answer = '像ChatGPT这样的智能对话系统，其核心技术是基于Transformer架构开发的。这种技术让AI能够更好地理解用户输入的长篇文字，记住对话上下文，并生成连贯自然的回复。相比早期的聊天机器人,在语言理解和表达流畅度上都有显著提升，这也是为什么现在AI对话感觉更智能、更像真人的重要原因'
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
    delay (ms) {
      return new Promise(resolve => setTimeout(resolve, ms))
    },
    async regenerateAnswer () {
      console.log('regenerating...')
      const lastMessage = this.chatMessages[this.chatMessages.length - 1]
      lastMessage.text = 'AI正在思考...'
      lastMessage.loading = true
      this.answerFinished = false
      let answer = ''
      let highlights = []
      console.log('file_reading_id', this.fileReadingID)
      await axios.post(this.$BASE_API_URL + '/study/reDoPaperStudy', {'file_reading_id': this.fileReadingID})
        .then((response) => {
          answer = response.data.ai_reply
          this.probQuestions = response.data.prob_question
          lastMessage.text = ''
          lastMessage.loading = false
          highlights = response.data.highlights
          lastMessage.highlights = highlights
        })
        .catch((error) => {
          console.error('Error:', error)
          lastMessage.text = ''
          answer = '抱歉, 无法从AI获取回应。'
          lastMessage.loading = false
          lastMessage.highlights = []
        })
      let cur = 0
      while (cur < answer.length) {
        lastMessage.text += answer.charAt(cur)
        cur++
        await this.delay(50)
      }
      this.answerFinished = true
    },
    sendProbQuestion (question) {
      this.chatInput = question
    },
    findReplySource () {
      if (this.docs.length === 0) {
        return
      }
      console.log('finding source...')
      this.answerFinished = false
      const sources = this.docs
      console.log('answer\'s source is...', this.docs)
      const lastMessage = this.chatMessages[this.chatMessages.length - 1]
      lastMessage.text += '\n来源: \n'
      let cnt = 1
      for (const source of sources) {
        const index1 = source.indexOf(']')
        const index2 = source.indexOf(']', index1 + 1)
        lastMessage.text += '[' + cnt + ']'
        lastMessage.text += source.substring(index2 + 1)
        lastMessage.text += '\n'
        cnt++
      }
      this.docs = []
      this.answerFinished = true
    },
    renderMarkdown () {
      // const md = markdownIt()
      console.log('document id is...', this.paperID)
      axios.post(this.$BASE_API_URL + '/study/generateAbstractReport', {document_id: this.paperID, paper_id: ''})
        .then((response) => {
          // if (response.data.summary) {
          //   const summary = response.data.summary
          //   this.markdownFile = md.render(summary)
          //   this.showSummaryModal = true
          // } else {
          //   this.$message({
          //     message: '正在为您生成总结，请稍后去个人中心查看...',
          //     type: 'warning'
          //   })
          //   this.summaryFinished = false
          // }
          this.$message({
            message: '正在为您生成总结，请稍后去个人中心查看...',
            type: 'warning'
          })
        })
        .catch(() => {
          this.$message({
            message: '生成摘要失败！',
            type: 'error'
          })
          this.summaryFinished = true
        })
    },
    clearHistory () {
      axios.post(this.$BASE_API_URL + '/study/clearConversation', {file_reading_id: this.fileReadingID})
        .then((response) => {
          if (response.status === 200) {
            this.$message({
              message: '清除历史对话成功！',
              type: 'success'
            })
            this.chatMessages = []
            this.probQuestions = []
            this.answerFinished = false
          }
        })
        .catch((error) => {
          console.error('清除对话失败', error)
        })
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
        await this.$axios.post(this.$BASE_API_URL + '/study/doPaperStudy', { 'query': chatMessage, 'file_reading_id': this.fileReadingID })
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
.my-header {
  display: flex;
  justify-content: space-between;
  /* padding: 20px; */
  align-items: center;
}

.chat-content {
  display: flex;
  flex-direction: column;
  align-items: stretch; /* 确保元素可以根据需要对齐到左边或右边 */
  background: rgb(233, 242, 251);
  width: 100%; /* 可以调整宽度以适应不同屏幕大小 */
  height: 100%;
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
  float: left;
  clear: both;
  border-radius: 0 15px 15px 15px;
}

.prob-question {
  background-color: white;
  color: black;
  border: 1px solid #ccc;
  border-radius: 10px;
  padding: 5px 20px;
  text-align: left;
  margin-bottom: 5px;
  font-size: small;
  max-width: 90%;
  cursor: pointer
}

/deep/ .highlight-word {
  text-decoration: underline wavy #1e90ff; /* 使用常见的蓝色 (DodgerBlue) */
  text-underline-offset: 2px;              /* 微调下划线的位置 */
  /* text-decoration-thickness: 2px;             加粗下划线 */
  cursor: pointer;
}

</style>
