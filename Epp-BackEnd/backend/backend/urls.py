
"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from business.api import auth, manage, paper_details, paper_interpret, paper_recommend, search, summary, upload_document, user_info, vector_database
from business.utils import paper_vdb_init

urlpatterns = [
                  path("admin/", admin.site.urls),

                  # 用户及管理员认证模块
                  path("api/login", auth.login),
                  path("api/sign", auth.signup),
                  path("api/testLogin", auth.testLogin),
                  path("api/logout", auth.logout),
                  path("api/managerLogin", auth.manager_login),
                  path("api/managerLogout", auth.manager_logout),

                  # 论文详情界面
                  path("api/userLikePaper", paper_details.like_paper),
                  path("api/userScoring", paper_details.score_paper),
                  path("api/collectPaper", paper_details.collect_paper),
                  path("api/reportComment", paper_details.report_comment),
                  path("api/commentPaper", paper_details.comment_paper),
                  path("api/batchDownload", paper_details.batch_download_papers),
                  path("api/getPaperInfo", paper_details.get_paper_info),
                  path("api/getComment1", paper_details.get_first_comment),
                  path("api/getComment2", paper_details.get_second_comment),
                  path("api/likeComment", paper_details.like_comment),
                  path("api/getUserPaperInfo", paper_details.get_user_paper_info),

                  path("api/saveNote", paper_details.save_paper_note),
                  path("api/getAnnotations", paper_details.get_paper_annotation),
                  path("api/deleteNote", paper_details.delete_paper_note),
                  path("api/reportAnnotation", paper_details.report_paper_annotation),



                  # 用户上传论文模块
                  path("api/uploadPaper", upload_document.upload_paper),
                  path("api/removeUploadedPaper", upload_document.remove_uploaded_paper),
                  path("api/userInfo/documents", upload_document.document_list),
                  path("api/getDocumentURL", upload_document.get_document_url),
                  path("api/downloadTranslated", upload_document.download_document_translated_url),

                  # 个人中心
                  path("api/userInfo/userInfo", user_info.user_info),
                  path("api/userInfo/avatar", user_info.modify_avatar),
                  path("api/userInfo/collectedPapers", user_info.collected_papers_list),
                  path('api/userInfo/delCollectedPapers', user_info.delete_collected_papers),
                  path("api/userInfo/searchHistory", user_info.search_history_list),
                  path("api/userInfo/delSearchHistory", user_info.delete_search_history),
                  path("api/userInfo/summaryReports", user_info.summary_report_list),
                  path("api/userInfo/delSummaryReports", user_info.delete_summary_reports),
                  path("api/userInfo/paperReading", user_info.paper_reading_list),
                  path("api/userInfo/delPaperReading", user_info.delete_paper_reading),
                  path("api/userInfo/notices", user_info.notification_list),
                  path("api/userInfo/readNotices", user_info.read_notification),
                  path("api/userInfo/delNotices", user_info.delete_notification),
                  path("api/userInfo/getSummary", user_info.get_summary_report),

                  # 管理端
                  path("api/manage/users", manage.user_list),
                  path("api/manage/papers", manage.paper_list),
                  path("api/manage/commentReports", manage.comment_report_list),
                  path("api/manage/commentReportDetail", manage.comment_report_detail),
                  path("api/manage/judgeCmtRpt", manage.judge_comment_report),
                  # path("api/manage/delComment", manage.delete_comment),
                  path("api/manage/userProfile", manage.user_profile),
                  path("api/manage/userStatistic", manage.user_statistic),
                  path("api/manage/paperOutline", manage.paper_outline),
                  path("api/manage/paperStatistic", manage.paper_statistic),
                  path("api/manage/serverStatus", manage.server_status),
                  path("api/manage/recordVisit", manage.record_visit),
                  path("api/manage/visitStatistic", manage.visit_statistic),
                  path("api/manage/userActiveOption", manage.user_active_option),
                  path("api/manage/promptwordStatistic", manage.hot_promptword_statistic),
                  path("api/manage/searchWordStatistic", manage.hot_searchword_statistic),
                  path("api/manage/autoCommentReports", manage.auto_comment_report_list),
                  path("api/manage/autoCommentReportDetail", manage.auto_comment_report_detail),


                  # 信息检索模块
                  path("api/search/easyVectorQuery", paper_vdb_init.easy_vector_query),
                  path("api/search/vectorQuery", search.vector_query),
                  path("api/search/dialogQuery", search.dialog_query),
                  path("api/search/flush", search.flush),
                  path("api/search/restoreSearchRecord", search.restore_search_record),
                  path("api/study/getUserSearchHistory", search.get_user_search_history),
                  path('api/search/rebuildKB', search.build_kb),
                  # path('api/search/getSearchRecord', get_search_record),
                  path('api/search/changeRecordPapers', search.change_record_papers),

                  # 向量化模块
                  # path("insert_vector_database", insert_vector_database),

                  # 文献研读模块
                  path("api/study/createPaperStudy", paper_interpret.create_paper_study),
                  path("api/study/restorePaperStudy", paper_interpret.restore_paper_study),
                  path("api/study/doPaperStudy", paper_interpret.do_paper_study),
                  path("api/study/getPaperPDF", paper_interpret.get_paper_url),
                  path("api/study/reDoPaperStudy", paper_interpret.re_do_paper_study),
                  path("api/study/clearConversation", paper_interpret.clear_conversation),
                  path("api/study/generateAbstractReport", summary.create_abstract_report),

                  # 本地向量库初始化
                  path("api/init/localVDBInit", paper_vdb_init.local_vdb_init),

                  # 综述摘要生成
                  path("api/summary/generateSummaryReport", summary.generate_summary),
                  path("api/summary/generateAbstractReport", summary.create_abstract_report),
                  path("api/summary/getSummaryStatus", summary.get_summary_status),

                  # 热门文献推荐
                  path("api/paperRecommend", paper_recommend.get_recommendation),
                  path("api/refresh", paper_recommend.get_recommendation)
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

