<template>
  <el-row style="overflow: hidden; height: 100vh;">
    <el-col :span="16" style="margin-top: 50px;">
      <!-- <iframe :src="pdfUrl" style="width: 100%; height: 755px;" frameborder="0"> -->
      <!-- </iframe> -->
      <div id="pdf-viewer-container" style="width: 100%; height: 755px;"></div>
      <!-- 下面加一个发表批注时候的框，来更美观 -->
      <el-dialog title="发表批注" :visible.sync="showCommentModal" width="50%" @close="closeCommentModal">
        <el-form>
            <el-form-item>
                <el-input type="textarea" placeholder="添加批注..." v-model="newComment" autosize>
                </el-input>
            </el-form-item>
        </el-form>
        <span slot="footer">
            <el-button @click="showCommentModal = false">取 消</el-button>
            <el-button type="primary" @click="submitComment('private')">私有批注</el-button>
            <el-button type="primary" @click="submitComment('public')">共有批注</el-button>
        </span>
      </el-dialog>
    </el-col>
    <el-col :span="8" style="margin-top: 50px">
      <!-- <read-assistant :paperID="paper_id" :fileReadingId="fileReadingID" /> -->
      <div style="margin-bottom: 20px;">
        <el-button @click="showReadAssistant = true" :type="showReadAssistant ? 'primary' : ''">阅读助手</el-button>
        <el-button @click="showReadAssistant = false" :type="!showReadAssistant ? 'primary' : ''">评论管理</el-button>
        <!-- <el-button @click="toggleTranslation" :type="isTranslated ? 'primary' : ''" class="special-button">
        {{ isTranslated ? '取消翻译' : '翻译全文' }}</el-button> -->
        <el-button type="text" icon="el-icon-download" @click="downloadPaper">下载翻译PDF</el-button>
      </div>
      <div v-if="showReadAssistant">
        <read-assistant :paperID="paper_id" :fileReadingId="fileReadingID" />
      </div>
      <div v-else>
        <!-- 这里放置评论展示与删除的，目前筛选还没实现，预计筛选后，用一个新的annotation数组来保存筛选后的注释，然后渲染到页面上,并且从数据库拿到的所有评论和筛选后的注释分别储存，方便随时切换 -->
        <!-- 新增的选择器和确认按钮 -->
      <div style="margin-bottom: 20px;">
        <el-select v-model="filterType" placeholder="筛选批注" @change="filterComments">
          <el-option label="全部" value="all"></el-option>
          <el-option label="我的批注" value="mine"></el-option>
          <el-option label="我的私有批注" value="minePrivate"></el-option>
          <el-option label="我的共有批注" value="minePublic"></el-option>
          <el-option label="他人批注" value="others"></el-option>
        </el-select>
        <el-select v-model="displayType" placeholder="显示类型" @change="filterComments">
          <el-option label="全部显示" value="all"></el-option>
          <el-option v-for="pageNum in allPageNumbers" :key="pageNum" :label="'第 ' + pageNum + ' 页'" :value="pageNum"></el-option>
        </el-select>
      </div>
        <div class="comment-container">
          <div v-for="annotation in annotations" :key="annotation.id">
            <div class="annotation">
              <div class="annotation-main">
                <div class="annotation-avatar">
                  {{ annotation.userName.charAt(0).toUpperCase() }}
                </div>
                <div class="annotation-body">
                  <div class="annotation-header">
                    <p class="annotation-username">{{ annotation.userName }}</p>
                    <p class="annotation-time">{{ formatDate(annotation.date) || '刚刚' }}</p>
                  </div>
                  <div class="annotation-content">
                    <p>{{ annotation.comment }}</p>
                  </div>
                </div>
              </div>
              <div class="annotation-actions">
                <div class="action-buttons">
                    <el-button type="text" class="annotation-jump" @click="scrollToPage(annotation.pageNum,annotation.y)">定位</el-button>

                    <div v-if="annotation.userName === currentUser">
                      <el-button type="text" class="danger-button" @click="deleteAnnotation(annotation.id)">删除</el-button>
                    </div>
                    <div v-else>
                      <el-button type="text" class="danger-button" @click="reportAnnotation(annotation.id)">举报</el-button>
                    </div>
                  </div>
                <el-dialog title="举报批注" :visible.sync="showReport" width="50%" @close="closeReport">
                  <el-form>
                      <el-form-item>
                          <el-input type="textarea" placeholder="添加举报理由..." v-model="reportReason" autosize>
                          </el-input>
                      </el-form-item>
                  </el-form>
                  <span slot="footer">
                      <el-button @click="showReport = false">取 消</el-button>
                      <el-button type="primary" @click="reportComment()">确认</el-button>
                  </span>
                </el-dialog>
              </div>
            </div>
          </div>
        </div>
        <!-- <div class="comment-container">
          <div v-for="annotation in annotations" :key="annotation.id" class="comment-item">
            <el-row>
              <el-col :span="2">
                <div class="date">{{ annotation.createdAt || '刚刚' }}</div>
                <div style="font-weight: bold;">{{ annotation.userName || '匿名用户' }}</div>
              </el-col>

              <el-col :span="22">
                <div class="comment-content">
                  <div class="my-footer">
                    <span class="actions">
                      <el-button type="text" v-if="annotation.userName === currentUser" @click="deleteAnnotation(annotation.id)">
                        删除
                      </el-button>
                      <el-button type="text" v-else @click="reportAnnotation(annotation.id)">
                        举报
                      </el-button>
                    </span>
                  </div>
                  <div class="text">{{ annotation.comment }}</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </div> -->
      </div>
    </el-col>
  </el-row>
</template>

<script>
import ReadAssistant from './ReadAssistant.vue'
import axios from 'axios'
export default {
  components: {
    'read-assistant': ReadAssistant
  },
  props: {
    paper_id: {
      type: String,
      default: ''
    }
  },
  data () {
    return {
      pdfUrl: '', // 用来显示的url
      originalUrl: '', // 用来保存原始PDF的URL
      translatedUrl: '', // 用来保存翻译后的PDF的URL
      fileReadingID: this.fileReadingID, // 自己赋值自己是什么毛病，但他原本代码就这样
      isSelecting: false, // 是否正在框选
      startX: 0, // 框选起始点的X坐标
      startY: 0, // 框选起始点的Y坐标
      selectionBox: null, // 保存框选区域的DOM元素
      annotations: [], // 保存用来显示的注释。初始等于下面，但是后续会根据筛选调整，保证论文和评论展示区都能只显示筛选后的注释
      allAnnotations: [], // 保存所有注释，每次渲染时从服务器获取即可，格式下面有样例
      pdfInstance: null, // PDF.js 实例
      containerOffsetTop: 0, // PDF 容器的顶部偏移
      containerOffsetLeft: 0, // PDF 容器的左侧偏移
      showReadAssistant: true, // 是否显示阅读助手
      currentUser: localStorage.getItem('username'), // 当前用户
      filterType: 'all', // 筛选类型
      displayType: 'all', // 显示类型
      allPageNumbers: [], // 所有页面的页码
      showCommentModal: false, // 是否显示发表批注框
      newComment: '', // 新批注内容
      isPublicComment: false, // 是否为公共批注
      pendingAnnotation: null, // 正在发表的批注内容
      isTranslated: false, // 是否翻译过
      showReport: false, // 是否显示举报框
      pendingAnnotationId: null, // 正在举报的批注ID
      reportReason: '', // 新举报理由
      isFetchPaperSuccess: false, // 是否获取成功
      isLoadPdfSuccess: false // 是否加载PDF成功
    }
  },
  created () {
    this.loadPDFJS() // 动态加载PDF.js库，即使pdfurl修改，也不需要重新加载
    this.fetchPaperPDF()
    this.fileReadingID = this.$route.query.fileReadingID
  },
  methods: {
    fetchPaperPDF () {
      axios.get(this.$BASE_API_URL + '/study/getPaperPDF?paper_id=' + this.paper_id)
        .then((response) => {
          this.originalUrl = this.$BASE_URL + response.data.local_url
          this.pdfUrl = this.originalUrl
          //   this.pdfUrl = '../../../static/Res3ATN -- Deep 3D Residual Attention Network for Hand Gesture  Recognition in Videos.pdf'
          console.log('论文PDF为', this.pdfUrl)
          // alert('论文PDF为' + this.pdfUrl)
          this.isFetchPaperSuccess = true
          if (this.isLoadPdfSuccess) {
            this.initPDFViewer()
          }
        })
        .catch((error) => {
          console.log('请求论文PDF失败 ', error)
          // alert('请求论文PDF失败 ' + error)
        })
    },
    // 动态加载PDF.js库
    loadPDFJS () {
      const script = document.createElement('script')
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.min.js'
      script.onload = () => {
        console.log('PDF.js 加载成功') // 添加这行
        window.pdfjsLib.GlobalWorkerOptions.workerSrc =
          'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.worker.min.js'
        this.isLoadPdfSuccess = true // PDF.js加载成功
        if (this.isFetchPaperSuccess) {
          this.initPDFViewer() // 确保PDF.js加载完成后再初始化查看器
        }
      }
      script.onerror = () => {
        console.error('PDF.js 加载失败') // 添加错误处理
      }
      document.head.appendChild(script)
    },
    // 初始化PDF查看器
    initPDFViewer () {
      if (!window.pdfjsLib) {
        console.error('PDF.js库未加载完成')
        return
      }

      const container = document.getElementById('pdf-viewer-container')
      container.innerHTML = '' // 清空容器
      container.style.position = 'relative' // 设为相对定位
      container.style.overflow = 'auto' // 添加滚动支持
      // window.pdfjsLib.getDocument(this.pdfUrl).promise
      //   .then(pdf => {
      //     this.pdfInstance = pdf
      //     this.renderAllPages(pdf, container)
      //     this.loadAnnotations() // 加载已有注释,同时顺便渲染一下
      //   })
      //   .catch(error => {
      //     console.error('PDF加载失败:', error)
      //   })
      window.pdfjsLib.GlobalWorkerOptions.workerSrc =
        'https://cdn.jsdelivr.net/npm/pdfjs-dist@2.10.377/build/pdf.worker.min.js'

      // 2. 加载PDF文档（含中文支持配置）
      window.pdfjsLib.getDocument({
        url: this.pdfUrl,
        cMapUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@2.10.377/cmaps/', // 关键：中文CMAP
        cMapPacked: true,
        useSystemFonts: true, // 禁用系统字体回退
        disableFontFace: false // 启用@font-face
      }).promise
        .then(pdf => {
          this.pdfInstance = pdf
          this.renderAllPages(pdf, container)
          this.loadAnnotations()
          // 可选：检查字体嵌入情况（调试用）
          // pdf.getPage(1).then(page => {
          //   page.getTextContent().then(textContent => {
          //     console.log('文档字体情况:', textContent.styles)
          //   })
          // })
        })
        .catch(error => {
          console.error('PDF加载失败:', error)
          // 友好错误提示（根据实际UI框架调整）
          if (error.name === 'MissingPDFException') {
            alert('PDF文件不存在或路径错误')
          } else if (error.name === 'InvalidPDFException') {
            alert('PDF文件已损坏')
          } else {
            alert('PDF加载失败，请确保文件使用标准字体嵌入')
          }
        })
      // 监听用户框选事件
      container.addEventListener('mousedown', this.handleMouseDown)
      container.addEventListener('mousemove', this.handleMouseMove)
      container.addEventListener('mouseup', this.handleMouseUp)
      container.addEventListener('scroll', this.updateAnnotationsPosition)
    },
    // 渲染所有页面
    renderAllPages (pdf, container) {
      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        this.allPageNumbers.push(pageNum)
        pdf.getPage(pageNum).then(page => {
          const viewport = page.getViewport({ scale: 1.5 })
          const canvas = document.createElement('canvas')
          const context = canvas.getContext('2d')
          canvas.height = viewport.height
          canvas.width = viewport.width
          // canvas.style.marginBottom = '10px' // 给每页之间加点间距
          container.appendChild(canvas)
          page.render({ canvasContext: context, viewport: viewport })
          canvas.setAttribute('data-page-num', pageNum)
          canvas.addEventListener('click', this.handlePageClick) // 处理点击事件（如框选或显示注释）
        })
      }
    },
    // 处理页面框选
    // 点击
    handleMouseDown (event) {
      if (this.isSelecting) return
      this.isSelecting = true
      const container = document.getElementById('pdf-viewer-container')
      this.startX = event.clientX + container.scrollLeft // 修正 scrollLeft
      this.startY = event.clientY + container.scrollTop // 修正 scrollTop

      this.containerOffsetTop = container.getBoundingClientRect().top
      this.containerOffsetLeft = container.getBoundingClientRect().left

      this.selectionBox = document.createElement('div')
      this.selectionBox.style.position = 'absolute'
      this.selectionBox.style.border = '2px dashed blue'
      this.selectionBox.style.pointerEvents = 'none'
      this.selectionBox.style.zIndex = '1000'
      container.appendChild(this.selectionBox)
    },
    handleMouseMove (event) {
      if (!this.isSelecting) return
      const container = document.getElementById('pdf-viewer-container')

      const width = event.clientX + container.scrollLeft - this.startX
      const height = event.clientY + container.scrollTop - this.startY // 修正 scrollTop

      this.selectionBox.style.left = `${this.startX - this.containerOffsetLeft}px`
      this.selectionBox.style.top = `${this.startY - this.containerOffsetTop}px`
      this.selectionBox.style.width = `${Math.abs(width)}px`
      this.selectionBox.style.height = `${Math.abs(height)}px`
      // this.selectionBox.style.left = `${Math.round(this.startX)}px`
      // this.selectionBox.style.top = `${Math.round(this.startY - this.containerOffsetTop)}px`
      // this.selectionBox.style.width = `${Math.round(Math.abs(width))}px`
      // this.selectionBox.style.height = `${Math.round(Math.abs(height))}px`
    },
    handleMouseUp (event) {
      if (!this.isSelecting) return

      this.isSelecting = false
      const selectionRect = this.selectionBox.getBoundingClientRect()
      document.getElementById('pdf-viewer-container').removeChild(this.selectionBox)
      this.selectionBox = null

      // 下面以后可以设置，当框太小或者太靠近滚动条等明显不是为了框选的时候，就不框选了。也就是不执行下面那行代码。
      this.extractSelectedText(selectionRect)
    },
    isIntersecting (rect1, rect2) {
      return !(rect2.top > rect1.bottom ||
              rect2.right < rect1.left ||
              rect2.bottom < rect1.top ||
              rect2.left > rect1.right)
    },
    extractSelectedText (selectionRect) {
      const container = document.getElementById('pdf-viewer-container')
      // 下面的这些坐标是 可能带小数的。其中上方相对视口偏移this.containerOffsetTop = container.getBoundingClientRect().top是永远不变的。有啥用我也不知道。。前四个确定了显示的框位置。滚动那个是确定相对位置的。container我用了相对距离，大概是考虑了不同浏览器的显示问题，有没有用就不知道了。但这里根本没用到页数了。
      // alert('选中区域：宽度：' + selectionRect.width + ' 高度：' + selectionRect.height + ' 左上角X坐标：' + selectionRect.left + ' 左上角Y坐标：' + selectionRect.top + '上方相对视口偏移:' + this.containerOffsetTop + '上下滚动距离' + container.scrollTop)
      const canvasElements = container.getElementsByTagName('canvas')

      for (let canvas of canvasElements) {
        const pageNum = parseInt(canvas.getAttribute('data-page-num'))
        const canvasRect = canvas.getBoundingClientRect()

        if (this.isIntersecting(selectionRect, canvasRect)) {
          this.showCommentDialog(selectionRect.left - canvasRect.left, selectionRect.top - canvasRect.top, selectionRect.width, selectionRect.height, pageNum)
          return
          // 这里直接return是因为，一个框选可以同时框两个页面，会执行两次，但我只需要一个页面的注释，所以直接return了。
        }
      }
    },

    // 下面的x,y,width,height,pageNum,comment都是相对于canvas的坐标。
    showCommentDialog (x, y, width, height, pageNum) {
      // const comment = prompt('请输入评论:')
      // if (comment) {
      //   const isPublic = confirm('是否公开评论？')
      //   this.saveAnnotation(x, y, width, height, pageNum, comment, isPublic)
      //   this.renderAnnotations() // 重新渲染所有注释，这里就不从数据库重新调了
      // }
      // 把参数临时保存起来，等待用户填写评论后再用
      this.pendingAnnotation = { x, y, width, height, pageNum }
      this.newComment = ''
      this.isPublicComment = true // 默认是公开
      this.showCommentModal = true
    },
    submitComment (type) {
      if (!this.newComment.trim()) {
        this.$message({
          message: '请输入批注内容',
          type: 'warning'
        })
        return
      }
      console.log(`提交${type === 'private' ? '私有' : '共有'}批注：`, this.newComment)
      const isPublic = type === 'public'
      const comment = this.newComment
      const { x, y, width, height, pageNum } = this.pendingAnnotation
      this.saveAnnotation(x, y, width, height, pageNum, comment, isPublic)
      this.closeCommentModal()
    },
    // 把一条注释渲染到页面上，这里的x,y,width,height,pageNum都是相对于canvas的坐标。
    // 具体来说，pageNum确定了页码。x,y是左上角坐标，width,height是宽高。并且这四个是相对于这一页的坐标。
    renderAnnotation (x, y, width, height, pageNum) {
      const container = document.getElementById('pdf-viewer-container')
      const canvas = container.querySelector(`canvas[data-page-num="${pageNum}"]`)
      if (!canvas) return
      // 创建虚线框
      const annotationBox = document.createElement('div')
      annotationBox.classList.add('annotation-box')
      annotationBox.style.position = 'absolute'
      annotationBox.style.left = `${canvas.offsetLeft + x}px`
      annotationBox.style.top = `${canvas.offsetTop + y}px`
      annotationBox.style.width = `${width}px`
      annotationBox.style.height = `${height}px`
      annotationBox.style.border = '2px dashed rgba(0, 0, 255, 0.8)' // 蓝色虚线框
      annotationBox.style.pointerEvents = 'auto' // 让鼠标事件生效
      annotationBox.style.zIndex = '1000'
      annotationBox.setAttribute('data-page-num', pageNum)

      // 创建弹出注释框
      const tooltip = document.createElement('div')
      tooltip.classList.add('annotation-tooltip')
      tooltip.style.position = 'absolute'
      tooltip.style.left = `${canvas.offsetLeft + x}px`
      tooltip.style.top = `${canvas.offsetTop + y + height + 5}px` // 显示在框下方
      tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.8)'
      tooltip.style.color = 'white'
      tooltip.style.padding = '6px 10px'
      tooltip.style.borderRadius = '5px'
      tooltip.style.fontSize = '12px'
      tooltip.style.whiteSpace = 'nowrap'
      tooltip.style.display = 'none'
      tooltip.setAttribute('data-page-num', pageNum)
      // tooltip.innerHTML = comments.map(c => `• ${c}`).join('<br>') // 显示所有注释

      // **鼠标悬停时，找到所有重叠的注释**
      annotationBox.addEventListener('mousemove', (event) => {
        // const overlappingComments = this.findOverlappingComments(x, y, width, height, pageNum)
        const overlappingComments = this.findOverlappingComments(event.clientX, event.clientY, pageNum)
        // tooltip.innerHTML = overlappingComments.map(c => `• ${c}`).join('<br>')
        tooltip.innerHTML = overlappingComments.map(c => `• ${c.userName}: ${c.comment}`).join('<br>')

        // **调整 tooltip 位置**
        tooltip.style.left = `${canvas.offsetLeft + x}px`
        tooltip.style.top = `${canvas.offsetTop + y + height + 5}px`
        tooltip.style.display = 'block'
        tooltip.style.textAlign = 'left'
        tooltip.style.whiteSpace = 'normal' // 允许换行
        tooltip.style.maxWidth = '400px' // 设置最大宽度
      })

      annotationBox.addEventListener('mouseleave', () => {
        tooltip.style.display = 'none'
      })

      container.appendChild(annotationBox)
      container.appendChild(tooltip)
    },
    findOverlappingComments (clientX, clientY, pageNum) {
      return this.annotations
        .filter(annotation => {
          const canvas = document.querySelector(`canvas[data-page-num="${pageNum}"]`)
          const canvasRect = canvas.getBoundingClientRect()
          const adjustX = clientX - canvasRect.left
          const adjustY = clientY - canvasRect.top // + canvas.scrollTop // 修正 scrollTop
          return annotation.pageNum === pageNum && this.isInBox(adjustX, adjustY, annotation.x, annotation.y, annotation.width, annotation.height)
        })
        .map(annotation => ({
          userName: annotation.userName, // 假设 annotation 对象中有一个 userName 属性
          comment: annotation.comment
        }))
    },

    isInBox (adjustX, adjustY, x, y, width, height) {
      return (adjustX >= x && adjustX <= x + width) && (adjustY >= y && adjustY <= y + height)
    },
    // 保存一条评论到数据库.
    // 这里的x,y,height,width都是相对于pageNum所在的canvas的坐标。（一页一个canvas）其中x，y是左上角坐标，width,height是宽高。并且这四个是相对于这一页的坐标。
    // 具体格式方面，x，y,width,height,都是小数，pageNum是整数（正整数，但不会很大，直接当整数就行）。comment是字符串。当然，小数那点误差不是很重要。
    // 强转整数也没太大事，但就小数表示吧。虽然是代表像素之类的 ，说是现在为了更精准显示，都是小数.
    saveAnnotation (x, y, width, height, pageNum, comment, isPublic) {
      // 就按照这个数据格式传就行，这里的x,y,height,width都是相对于pageNum所在的canvas的坐标。（一页一canvas）
      axios.post(this.$BASE_API_URL + '/study/saveNote', {
        params: {
          x, y, width, height, pageNum, comment, paper_id: this.paper_id, isPublic // 虽然没传username，但是后端要存
          // 后端可以在session里取出username,暂时不管评论时间？
        }
      }).then(response => {
        console.log('保存注释成功', response)
        // window.location.reload()// 刷新页面，重新渲染所有注释，因为注释的id是后端生成的，只能重新从后端获取。
        // 当前，也可以在这个response里，把新加的注释的id返回给前端，前端再把id存到本地，这样就不用重新刷新页面了。
        const annotation = { x, y, width, height, pageNum, comment, userName: this.currentUser, isPublic, id: response.data.id } // 假设 annotation 对象中有一个 id 属性,也就是主键，1,2,3，自增。
        // this.annotations.push(annotation)// 新加的注释已经保存到前端本地。
        this.allAnnotations.push(annotation) // 新加的注释已经保存到本地数组。
        this.annotations = this.allAnnotations
        this.renderAnnotations() // 重新渲染所有注释，这里就不从数据库重新调了
        this.$message({
          message: '添加批注成功',
          type: 'success'
        })
      }).catch(error => {
        console.error('保存注释失败', error)
        this.$message({
          message: error.response.data.message || '保存注释失败',
          type: 'error'
        })
      })
    },
    // 重新渲染所有注释，也就是删除旧的注释框，重新渲染新的注释框。也就是对每个公开或自己的评论分别renderAnnotation。
    renderAnnotations () {
      const container = document.getElementById('pdf-viewer-container')
      container.querySelectorAll('.annotation-box, .annotation-tooltip').forEach(el => el.remove()) // 清除旧的注释框
      this.annotations.forEach(annotation => {
        const { x, y, width, height, pageNum, comment, userName, isPublic, id } = annotation
        console.log(comment, userName, isPublic, id)
        this.renderAnnotation(x, y, width, height, pageNum)
      })

      // 添加窗口调整大小事件监听器
      window.addEventListener('resize', this.handleResize)
    },
    // 处理窗口调整大小的事件
    handleResize () {
      this.renderAnnotations() // 重新渲染注释
    },
    // 从数据库加载所有已有评论，并渲染到页面上，可以分别renderAnnotation,也可以直接renderAnnotations
    // 这个只在开始调用一次，避免和数据库交互太多，影响性能。
    // 要求，后端需要返回一个数组，每个元素是一条注释，格式如下：
    // {
    //   x: 0.1, // 小数，相对于pageNum所在的canvas的坐标
    //   y: 0.2, // 小数，相对于pageNum所在的canvas的坐标
    //   width: 0.3, // 小数，相对于pageNum所在的canvas的坐标
    //   height: 0.4, // 小数，相对于pageNum所在的canvas的坐标
    //   pageNum: 1, // 整数，页码
    //   comment: '这是一条评论', // 字符串
    //   userName: '用户名', // 字符串
    //   isPublic: true // 布尔值，是否公开true/false
    // }
    // 同时，后端可以根据session里的username来判断是否是自己的评论，只能返回自己的评论和他人的公开评论。
    loadAnnotations () {
      axios.get(this.$BASE_API_URL + '/study/getAnnotations?paper_id=' + this.paper_id)
        .then(response => {
          this.allAnnotations = response.data.annotations
          this.annotations = this.allAnnotations
          this.renderAnnotations() // 直接渲染所有注释，这里就不从数据库重新调了
        }).catch(error => {
          console.error('加载注释失败', error)
        })
    },
    deleteAnnotation (annotationId) {
      this.annotations = this.annotations.filter(annotation => annotation.id !== annotationId) // 从本地数组中删除注释
      this.allAnnotations = this.allAnnotations.filter(annotation => annotation.id !== annotationId) // 从本地数组中删除注释
      this.renderAnnotations() // 重新渲染所有注释，这里就不从数据库重新调了
      // TODO 可以把删除注释的放在post返回结果后再进行，但是我相信他会删成功，就直接这样了.
      axios.post(this.$BASE_API_URL + '/study/deleteNote', { 'annotation_id': annotationId })
        .then(response => {
          this.$message({
            message: '删除批注成功',
            type: 'success'
          })
          // this.loadAnnotations() // 重新加载注释
        }).catch(error => {
          console.error('删除批注失败', error)
          this.$message({
            message: '删除批注失败',
            type: 'error'
          })
        })
    },
    reportAnnotation (annotationId) {
      // const reason = prompt('请输入举报理由:') // 弹出提示框，让用户输入举报理由
      this.pendingAnnotationId = annotationId
      this.showReport = true
    },
    reportComment () {
      if (!this.reportReason.trim()) {
        this.$message({
          message: '请输入举报理由',
          type: 'warning'
        })
        return
      }
      console.log(this.reportReason)
      const reason = this.reportReason
      const annotationId = this.pendingAnnotationId
      // alert('举报理由：' + reason + '，批注ID：' + annotationId)
      axios.post(this.$BASE_API_URL + '/study/reportAnnotation', { 'annotation_id': annotationId, 'reason': reason })
        .then(response => {
          this.$message({
            message: '举报批注成功,请等管理员处理',
            type: 'success'
          })
          // this.loadAnnotations() // 重新加载注释
        }).catch(error => {
          console.error('举报批注失败', error)
          this.$message({
            message: '举报批注失败',
            type: 'error'
          })
        })
      this.closeReport()
    },
    closeReport () {
      this.showReport = false
      this.pendingAnnotationId = null
      this.reportReason = ''
    },
    filterComments () {
      this.annotations = this.allAnnotations.filter(annotation => {
        // 根据筛选类型过滤
        if (this.filterType === 'mine') {
          return annotation.userName === this.currentUser
        } else if (this.filterType === 'others') {
          return annotation.userName !== this.currentUser
        } else if (this.filterType === 'minePrivate') {
          return annotation.userName === this.currentUser && !annotation.isPublic // 只显示私有批注
        } else if (this.filterType === 'minePublic') {
          return annotation.userName === this.currentUser && annotation.isPublic // 只显示公开批注
        } else if (this.filterType === 'all') {
          return true // 全部
        } else {
          return true // 全部
        }
      }).filter(annotation => {
        // 根据显示类型过滤
        if (this.displayType !== 'all') {
          return annotation.pageNum === this.displayType // 假设currentPage是当前显示的页码
        } else {
          return true // 全部显示
        }
      })
      this.renderAnnotations() // 重新渲染所有注释，这里就不从数据库重新调了
    },
    closeCommentModal () {
      this.showCommentModal = false
      this.newComment = ''
    },
    toggleTranslation () {
      this.isTranslated = !this.isTranslated
      if (this.isTranslated) {
        this.translateAllText()
      } else {
        this.restoreOriginalText()
      }
    },
    translateAllText () {
      axios.get(this.$BASE_API_URL + '/study/getDocumentTranslatedURL?document_id=' + this.paper_id)// 这里的路径和下面的冲了，但是这个方法不会调用，所以没问题
        .then((response) => {
          this.translatedUrl = this.$BASE_URL + response.data.local_url
          this.pdfUrl = this.translatedUrl
          //   this.pdfUrl = '../../../static/Res3ATN -- Deep 3D Residual Attention Network for Hand Gesture  Recognition in Videos.pdf'
          console.log('论文PDF为', this.pdfUrl)
          this.initPDFViewer()
        })
        .catch((error) => {
          console.log('请求论文PDF失败 ', error)
        })
    },
    downloadPaper () {
      // 实现下载功能
      axios.get(this.$BASE_API_URL + '/study/downloadTranslated?document_id=' + this.paper_id)
        .then((response) => {
          if (response.data.is_success === true) {
            this.$message({
              message: '开始下载！',
              type: 'success'
            })
            const zipUrl = this.$BASE_URL + response.data.zip_url
            const link = document.createElement('a')
            link.href = zipUrl
            link.download = 'papers.zip'
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
          }
        })
        .catch((error) => {
          console.error('Error:', error)
        })
    },
    restoreOriginalText () {
      this.pdfUrl = this.originalUrl
      this.initPDFViewer()
    },
    formatDate (date) {
      if (!date) return ''
      const [d, t] = date.split('T')
      return `${d}\n${t.slice(0, 8)}` // 只保留到秒
    },
    scrollToPage (pageNum, y) {
      const container = document.getElementById('pdf-viewer-container')
      const canvas = container.querySelector(`canvas[data-page-num="${pageNum}"]`)
      if (!canvas) return

      // 获取目标canvas元素的顶部位置
      const targetTop = Math.max(0, canvas.offsetTop + y - 20)

      // 平滑滚动到目标位置
      container.scroll({
        top: targetTop,
        behavior: 'smooth'
      })
    }
  }
}
</script>

<style scoped>

.comment-container {
  overflow-y: auto;
  height: calc(100vh - 220px);
  padding: 10px;
  background-color: #f4f4f5;
}

.annotation {
  background-color: #fff;
  padding: 14px;
  border-radius: 10px;
  margin-bottom: 16px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.05);
}

/* 主体部分：头像 + 内容 */
.annotation-main {
  display: flex;
  gap: 14px;
}

/* 左侧头像 */
.annotation-avatar {
  width: 60px;
  height: 60px;
  min-width: 60px;
  border-radius: 50%;
  background-color: #409EFF;
  color: #fff;
  font-size: 24px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 中间部分：用户名 + 时间 + 评论内容 */
.annotation-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 顶部信息栏：用户名和时间 */
.annotation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.annotation-username {
  margin: 0;
  font-weight: 600;
  font-size: 15px;
  color: #333;
}

.annotation-time {
  font-size: 12px;
  color: #999;
  margin: 0;
}

/* 评论内容 */
.annotation-content p {
  font-size: 14px;
  color: #444;
  margin: 6px 0 0 0;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 操作按钮区域 */
.annotation-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 跳转按钮简洁风格 */
.annotation-jump {
  font-size: 13px;
  color: #409EFF;
  background: none;
  border: none;
  padding: 2px 4px;
  cursor: pointer;
  line-height: 1; /* 与 el-button 保持一致 */
}

.annotation-jump:hover {
  text-decoration: underline;
}

/* 红色按钮统一样式（删除/举报） */
.danger-button {
  color: #f56c6c !important;
  font-size: 13px;
  background: none;
  border: none;
  padding: 2px 4px;
  cursor: pointer;
  line-height: 1; /* 与 el-button 保持一致 */
}

.danger-button:hover {
  background-color: #fde2e2;
}

/* .annotation {
display: flex;
justify-content: space-between;
align-items: center;
border: 1px solid #ccc;
padding: 8px 12px;
margin-bottom: 10px;
border-radius: 5px;
background-color: #f9f9f9;
}

.annotation-User {
line-height: 1.4;
}
.annotation-time {
font-size: 13px;
color: #888;
margin: 0;
}
.annotation-User p {
margin: 0;
font-weight: 500;
}

.annotation-content {
flex-grow: 1;
}

.annotation-actions {
display: flex;
gap: 10px;
}

.annotation-content p {
margin: 0;
}
.comment-container {
overflow-y: auto;
height: calc(100vh - 50px - 20px - 150px);
} */

.special-button {
background-color: #ff9900;
border-color: #ff9900;
color: white;
}

.special-button:hover {
background-color: #ff7f00; /* 自定义悬停背景颜色 */
border-color: #ff7f00; /* 自定义悬停边框颜色 */
}

.special-button:focus {
border-color: #ff7f00; /* 自定义聚焦边框颜色 */
box-shadow: 0 0 0 3px rgba(255, 127, 0, 0.3); /* 自定义聚焦阴影 */
}
</style>
