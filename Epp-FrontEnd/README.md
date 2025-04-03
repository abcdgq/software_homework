# Epp-FrontEnd


管理端用户名admin
密码ruangong


对Epp-FrontEnd\Frontend\Epp_FrontEnd\src\components\PaperRead\LocalPaperReader.vue文件进行修改，引入pdfjs，使其可以显示本地pdf文件了。（这个对应用户端全文解读，本地上传pdf后，在文件库点击文件名（蓝色）之后进入的页面。。原本是无法显示pdf的（包括其他页面也无法显示，主要是因为他是在前端用一个方式显示后端的pdf文件，但是跨域了，并且这个跨域，在后端setting里改了半天，他都还是不允许跨（因为简单的允许跨域“嵌入”显示方法由于安全问题被淘汰了）。


现在，那个里面的pdf可以显示出来了，并且简单了添加了点击添加注释功能（点击后弹出一个输入框，输入内容后点击确定）。，但是对输入的内容还没有做任何处理，同时，仅仅只是简单记录了点击的屏幕相对位置（x=123，y=456），还没有做任何处理。。后续至少要把这个点击修改，因为pdf是可以滚动的，一滚，相对位置就变了，当然，后续可以看有没有相对整个pdf的相对位置。。。不过如果更美观可能会是框选，记录左上到右下两个点，但这个应该容易。当然，更没有做注释显示功能。





本来试了半天的pdfjs-dist来显示pdf，但是各种版本都会受到本地已有的babel的版本过低以及各种奇奇怪怪的版本问题，所以采用直接'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.worker.min.js'的方式引入pdfjs，，，即不在本地下载这玩意了，直接网上导入。。应该不需要安装任何东西就可以。

Epp-FrontEnd\Frontend\Epp_FrontEnd\src\components\PaperRead\LocalPaperReader.vue文件修改如下：
现在可以对框选内容悬置鼠标时候，自动显示所有包含该鼠标点的框的注释，剩下的工作只有，在save和load，Annotation里添加与数据库交互的代码了，以及确保开局就自动把所有注释显示出来即可（需要有一个save函数框架了）
loadAnnotations和saveAnnotation函数解决（只剩下与后端交互了），就可以实现注释的保存和加载了。

同时，需要进行完善，比如每个评论或许可以同时储存和显示来源（比如时间，发送者，加举报功能，之类的，当然，举报可以都交给自动审核，不允许人工举报，就方便了）

以及，可以加入一个按钮，按了之后就清空annotations，和重新渲染，一个按钮是重新loadAnnotations，便于用户体验，这种任务量应该很小。

<!-- npm install --save pdfjs-dist/legacy/build/pdf -->


<!-- npm install pdfjs-dist -->
<!-- npm install --save-dev @babel/plugin-proposal-private-methods @babel/plugin-proposal-private-property-in-object -->

<!-- npm install pdfjs-dist@2.10.377

npm update babel-loader @babel/core @babel/plugin-proposal-optional-chaining
npm install @babel/plugin-proposal-optional-chaining --save-dev



npm uninstall babel-core --save-dev
npm install --save-dev @babel/core@latest @babel/cli@latest @babel/plugin-proposal-class-properties@latest @babel/preset-env@latest
npm install --save-dev babel-loader@latest
npm install --save-dev vue-loader@latest -->
