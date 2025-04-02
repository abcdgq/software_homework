<template>
    <el-row style="overflow: hidden; height: 100vh;">
      <el-col :span="16" style="margin-top: 60px;">
        <!-- <iframe :src="pdfUrl" style="width: 100%; height: 755px;" frameborder="0"> -->
        <!-- </iframe> -->
        <div id="pdf-viewer-container" style="width: 100%; height: 755px;"></div>
      </el-col>
      <el-col :span="8" style="margin-top: 60px">
        <read-assistant :paperID="paper_id" :fileReadingId="fileReadingID" />
      </el-col>
    </el-row>
</template>

<script>
import ReadAssistant from './LocalReadAssistant.vue'
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
      pdfUrl: '',
      fileReadingID: '',
      isSelecting: false, // 是否正在框选
      startX: 0, // 框选起始点的X坐标
      startY: 0, // 框选起始点的Y坐标
      selectionBox: null, // 保存框选区域的DOM元素
      annotations: [], // 保存注释
      pdfInstance: null, // PDF.js 实例
      containerOffsetTop: 0 // PDF 容器的顶部偏移
    }
  },
  created () {
    this.fetchPaperPDF()
    this.fileReadingID = this.$route.query.fileReadingID
    this.loadPDFJS()
  },
  methods: {
    fetchPaperPDF () {
      axios.get(this.$BASE_API_URL + '/getDocumentURL?document_id=' + this.paper_id)
        .then((response) => {
          this.pdfUrl = this.$BASE_URL + response.data.local_url
          //   this.pdfUrl = '../../../static/Res3ATN -- Deep 3D Residual Attention Network for Hand Gesture  Recognition in Videos.pdf'
          console.log('论文PDF为', this.pdfUrl)
          this.initPDFViewer()
        })
        .catch((error) => {
          console.log('请求论文PDF失败 ', error)
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
      window.pdfjsLib.getDocument(this.pdfUrl).promise
        .then(pdf => {
          this.pdfInstance = pdf
          this.renderAllPages(pdf, container)
          this.loadAnnotations() // 加载已有注释
        })
        .catch(error => {
          console.error('PDF加载失败:', error)
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
        pdf.getPage(pageNum).then(page => {
          const viewport = page.getViewport({ scale: 1.5 })
          const canvas = document.createElement('canvas')
          const context = canvas.getContext('2d')
          canvas.height = viewport.height
          canvas.width = viewport.width
          canvas.style.marginBottom = '10px' // 给每页之间加点间距
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
      this.startX = event.clientX
      this.startY = event.clientY + container.scrollTop // 修正 scrollTop

      this.containerOffsetTop = container.getBoundingClientRect().top

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

      const width = event.clientX - this.startX
      const height = event.clientY + container.scrollTop - this.startY // 修正 scrollTop

      this.selectionBox.style.left = `${this.startX}px`
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
      alert('选中区域：宽度：' + selectionRect.width + ' 高度：' + selectionRect.height + ' 左上角X坐标：' + selectionRect.left + ' 左上角Y坐标：' + selectionRect.top + '上方相对视口偏移:' + this.containerOffsetTop + '上下滚动距离' + container.scrollTop)
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
      const comment = prompt('请输入评论:')

      if (comment) {
        this.saveAnnotation(x, y, width, height, pageNum, comment)
        this.renderAnnotation(x, y, width, height, pageNum, comment)
      }
    },
    // 把一条注释渲染到页面上，这里的x,y,width,height,pageNum都是相对于canvas的坐标。
    // 具体来说，pageNum确定了页码。x,y是左上角坐标，width,height是宽高。并且这四个是相对于这一页的坐标。
    renderAnnotation (x, y, width, height, pageNum, comment) {
      const container = document.getElementById('pdf-viewer-container')
      const canvas = container.querySelector(`canvas[data-page-num="${pageNum}"]`)
      if (!canvas) return

      const annotation = document.createElement('div')
      annotation.classList.add('annotation')
      annotation.style.position = 'absolute'
      annotation.style.left = `${canvas.offsetLeft + x}px`
      annotation.style.top = `${canvas.offsetTop + y}px`
      annotation.style.width = `${width}px`
      annotation.style.height = `${height}px`
      annotation.style.backgroundColor = 'rgba(0,0,0,0.7)'
      annotation.style.color = 'white'
      annotation.style.padding = '5px'
      annotation.style.borderRadius = '5px'
      annotation.style.fontSize = '12px'
      annotation.textContent = comment
      annotation.setAttribute('data-page-num', pageNum)

      container.appendChild(annotation)
    },

    // 保存一条评论到数据库，具体逻辑还没写，等前端显示好看了再说。
    saveAnnotation (x, y, width, height, pageNum, comment) {

    },
    // 从数据库加载所有已有评论，并渲染到页面上，也就是对每个公开或自己的评论分别renderAnnotation。
    loadAnnotations () {
      // axios.get(this.$BASE_API_URL + '/getAnnotations', {
      //   params: { fileReadingID: this.fileReadingID }
      // }).then(response => {
      //   this.annotations = response.data.annotations
      //   this.annotations.forEach(annotation => {
      //     this.renderAnnotation(annotation.x, annotation.y, annotation.pageNum, annotation.comment)
      //   })
      // }).catch(error => {
      //   console.error('加载注释失败', error)
      // })
    }
  }
}
</script>

<style scoped>

</style>
