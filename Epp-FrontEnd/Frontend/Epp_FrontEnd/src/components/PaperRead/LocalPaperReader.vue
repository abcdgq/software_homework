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
      fileReadingID: ''
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
      container.style.overflow = 'auto' // 添加滚动支持
      window.pdfjsLib.getDocument(this.pdfUrl).promise
        .then(pdf => {
          this.renderAllPages(pdf, container)
        })
        .catch(error => {
          console.error('PDF加载失败:', error)
        })
      // 监听用户点击事件，添加注释
      container.addEventListener('click', event => {
        const rect = container.getBoundingClientRect()
        const x = event.clientX - rect.left
        const y = event.clientY - rect.top
        const comment = prompt('请输入评论内容')
        console.log('用户点击坐标:', x, y, '评论内容:', comment)
      })
      // window.pdfjsLib.getDocument(this.pdfUrl).promise
      //   .then(pdf => {
      //     // 渲染第一页
      //     return pdf.getPage(1)
      //   })
      //   .then(page => {
      //     const viewport = page.getViewport({ scale: 1.5 })
      //     const canvas = document.createElement('canvas')
      //     const context = canvas.getContext('2d')
      //     canvas.height = viewport.height
      //     canvas.width = viewport.width
      //     container.appendChild(canvas)

      //     return page.render({
      //       canvasContext: context,
      //       viewport: viewport
      //     }).promise
      //   })
      //   .catch(error => {
      //     console.error('PDF渲染错误:', error)
      //   })
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
        })
      }
    }
  }
}
</script>

<style scoped>

</style>
