"""
    论文详情页相关接口
"""
import json
import os
import random
import time
import zipfile
import PyPDF2

from backend.settings import BATCH_DOWNLOAD_PATH, BATCH_DOWNLOAD_URL
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from business.models import User, Paper, PaperScore, CommentReport, FirstLevelComment, SecondLevelComment, Notification, \
    AnnotationReport, UserDocument, DocumentNote
from business.models.auto_check_record import AutoCheckRecord
from business.models.auto_check_risk import AutoRiskRecord
from business.models.auto_check_undo import AutoUndoRecord
from business.models.auto_note_check_record import AutoNoteCheckRecord
from business.models.auto_note_check_risk import AutoNoteRiskRecord
from business.models.paper_annotation import FileAnnotation
from business.models.paper_note import FileNote
from business.utils import reply
from business.utils.download_paper import downloadPaper
from scripts.aliyun_test import auto_comment_detection
from scripts.pdf_translate_test import pdf_translate
from scripts.text_translate_test import connect as text_translate_tool

if not os.path.exists(BATCH_DOWNLOAD_PATH):
    os.makedirs(BATCH_DOWNLOAD_PATH)


def like_paper(request):
    """
    点赞/取消点赞文献
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.session.get('username')
        paper_id = data.get('paper_id')
        user = User.objects.filter(username=username).first()
        paper = Paper.objects.filter(paper_id=paper_id).first()
        liked = user.liked_papers.filter(paper_id=paper_id).first()
        # 取消点赞
        if liked:
            user.liked_papers.remove(paper)
            paper.like_count -= 1
            user.save()
            paper.save()
            return JsonResponse({'message': '取消点赞成功', 'is_success': True})
        # 点赞
        if user and paper:
            user.liked_papers.add(paper)
            paper.like_count += 1
            user.save()
            paper.save()
            return JsonResponse({'message': '点赞成功', 'is_success': True})
        else:
            return JsonResponse({'error': '用户或文献不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def score_paper(request):
    """
    文献评分
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.session.get('username')
        paper_id = data.get('paper_id')
        score = data.get('score')
        user = User.objects.filter(username=username).first()
        paper = Paper.objects.filter(paper_id=paper_id).first()
        paper_score = PaperScore.objects.filter(user_id=user, paper_id=paper).first()
        # 判断用户是否对该文献进行过评分
        if paper_score:
            return JsonResponse({'error': '用户已对该文献进行过评分', 'is_success': False}, status=400)
        # 判断评分是否在1到5之间，且为整数
        if not isinstance(score, int) or score < 1 or score > 5:
            return JsonResponse({'error': '评分应为0到10之间的整数', 'is_success': False}, status=400)
        # 存储评分，更新文献平均分，保留两位小数
        if user and paper:
            paper_score = PaperScore(user_id=user, paper_id=paper, score=score)
            paper_score.save()
            paper.score_count += 1
            paper.score = round((paper.score * (paper.score_count - 1) + score) / paper.score_count, 2)
            paper.save()
            return JsonResponse({'message': '评分成功', 'is_success': True})
        else:
            return JsonResponse({'error': '用户或文献不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def collect_paper(request):
    """
    收藏/取消收藏文献
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.session.get('username')
        paper_id = data.get('paper_id')
        user = User.objects.filter(username=username).first()
        paper = Paper.objects.filter(paper_id=paper_id).first()
        collected = user.collected_papers.filter(paper_id=paper_id).first()
        # 取消收藏
        if collected:
            user.collected_papers.remove(paper)
            paper.collect_count -= 1
            user.save()
            paper.save()
            return JsonResponse({'message': '取消收藏成功', 'is_success': True})
        # 收藏
        if user and paper:
            user.collected_papers.add(paper)
            paper.collect_count += 1
            user.save()
            paper.save()
            return JsonResponse({'message': '收藏成功', 'is_success': True})
        else:
            return JsonResponse({'error': '用户或文献不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def report_comment(request):
    """
    举报评论
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.session.get('username')
        comment_id = data.get('comment_id')
        comment_level = data.get('comment_level')
        report = data.get('report')
        user = User.objects.filter(username=username).first()
        # 这里需要知道是一级评论还是二级评论
        comment = None
        if comment_level == 1:
            comment = FirstLevelComment.objects.filter(comment_id=comment_id).first()
        elif comment_level == 2:
            comment = SecondLevelComment.objects.filter(comment_id=comment_id).first()
        if user and comment:
            if comment_level == 1:
                # 一级评论
                report_com = CommentReport(comment_id_1=comment, comment_level=1, user_id=user, content=report)
                report_com.save()
            elif comment_level == 2:
                # 二级评论
                report_com = CommentReport(comment_id_2=comment, comment_level=2, user_id=user, content=report)
                report_com.save()
            return JsonResponse({'message': '举报成功', 'is_success': True})
        else:
            return JsonResponse({'error': '用户或评论不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def comment_paper(request):
    """
    用户评论（含一级、二级评论）
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.session.get('username')
        paper_id = data.get('paper_id')
        comment_level = data.get('comment_level')  # 1 / 2
        text = data.get('comment')
        user = User.objects.filter(username=username).first()
        paper = Paper.objects.filter(paper_id=paper_id).first()
        if user and paper:
            if comment_level == 1:
                comment = FirstLevelComment(user_id=user, paper_id=paper, text=text)
                comment.save()
                # 启动自动审核程序
                if_success, status_code, labels, reason = auto_comment_detection(text)
                print("labels:")
                print(labels)
                print(type(labels))
                if if_success:
                    auto_record = AutoCheckRecord(comment_id_1=comment, comment_level=1, labels=labels, reason=reason)
                    auto_record.save()

                    safe = True
                    if len(labels) == 0 or labels.isspace():
                        comment.visibility = True
                        auto_record.security = True
                        comment.save()
                        auto_record.save()
                    else:
                        # 将不安全审核记录到表中
                        safe = False
                        risk_record = AutoRiskRecord(check_record=auto_record)
                        risk_record.save()
                else:
                    # 将未成功自动审核的评论记录
                    undo_record = AutoUndoRecord(comment_id_1=comment, comment_level=1)
                    undo_record.save()

            elif comment_level == 2:
                level1_comment_id = data.get('level1_comment_id')
                level1_comment = FirstLevelComment.objects.filter(comment_id=level1_comment_id).first()
                # 如果是回复二级评论的评论，获取其回复的二级评论的id
                reply_comment_id = data.get('reply_comment_id')
                reply_comment = None
                if reply_comment_id:
                    reply_comment = SecondLevelComment.objects.filter(comment_id=reply_comment_id).first()
                comment = SecondLevelComment(user_id=user, paper_id=paper, text=text, level1_comment=level1_comment,
                                             reply_comment=reply_comment)
                comment.save()
                # 启动自动审核程序
                if_success, status_code, labels, reason = auto_comment_detection(text)
                if if_success:
                    auto_record = AutoCheckRecord(comment_id_2=comment, comment_level=2, labels=labels,
                                                  reason=reason)
                    auto_record.save()

                    safe = True
                    if len(labels) == 0 or labels.isspace():
                        comment.visibility = True
                        auto_record.security = True
                        comment.save()
                        auto_record.save()
                    else:
                        safe = False
                        # 将不安全审核记录到表中
                        risk_record = AutoRiskRecord(auto_record)
                        risk_record.save()
                else:
                    # 将未成功自动审核的评论记录
                    undo_record = AutoUndoRecord(comment_id_2=comment.comment_id, comment_level=2)
                    undo_record.save()

            paper.comment_count += 1
            paper.save()
            if safe:
                return JsonResponse({'message': '评论成功', 'is_success': True})
            else:
                return JsonResponse({'message': '评论存在不适合展示的内容：' + json.loads(reason)['riskTips'] if 'riskTips' in reason else labels, 'is_success': False})
        else:
            return JsonResponse({'error': '用户或文献不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def get_first_comment(request):
    """
    获取一级评论
    """
    if request.method == 'GET':
        username = request.session.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            return JsonResponse({'error': '用户未登录', 'is_success': False}, status=400)
        paper_id = request.GET.get('paper_id')
        comments = FirstLevelComment.objects.filter(paper_id=paper_id)
        data = []
        for comment in comments:
            if comment.visibility is False:
                continue
            second_len = SecondLevelComment.objects.filter(level1_comment_id=comment.comment_id).count()
            data.append({
                'comment_id': comment.comment_id,
                'date': comment.date.strftime("%Y-%m-%d %H:%M:%S"),
                'text': comment.text,
                'like_count': comment.like_count,
                'username': comment.user_id.username,
                'user_image': comment.user_id.avatar.url,
                'user_liked': comment.liked_by_users.filter(username=user).first() is not None,
                'second_len': second_len
            })
        total = len(data)
        return JsonResponse({'message': '获取成功', 'total': total, 'comments': data, 'is_success': True})
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def get_second_comment(request):
    """
    获取二级评论
    """
    if request.method == 'GET':
        username = request.session.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            return JsonResponse({'error': '用户未登录', 'is_success': False}, status=400)
        level1_comment_id = request.GET.get('comment1_id')
        if (level1_comment_id == 'undefined' or level1_comment_id is None):
            return JsonResponse({'error': '一级评论ID不能为空', 'is_success': False}, status=400)
        comments = SecondLevelComment.objects.filter(level1_comment_id=level1_comment_id)
        data = []
        for comment in comments:
            if comment.level1_comment.visibility is False:
                continue
            if comment.reply_comment and comment.reply_comment.visibility is False:
                continue
            if comment.visibility is False:
                continue
            data.append({
                'comment_id': comment.comment_id,
                'date': comment.date.strftime("%Y-%m-%d %H:%M:%S"),
                'text': comment.text,
                'like_count': comment.like_count,
                'to_username': comment.reply_comment.user_id.username if comment.reply_comment else None,
                'username': comment.user_id.username,
                'user_image': comment.user_id.avatar.url,
                'user_liked': comment.liked_by_users.filter(username=user).first() is not None
            })
        return JsonResponse({'message': '获取成功', 'comments': data, 'is_success': True})
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def like_comment(request):
    """
    点赞评论/取消点赞评论
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.session.get('username')
        comment_id = data.get('comment_id')
        comment_level = data.get('comment_level')
        user = User.objects.filter(username=username).first()
        # 这里需要知道是一级评论还是二级评论
        comment = None
        if comment_level == 1:
            comment = FirstLevelComment.objects.filter(comment_id=comment_id).first()
        elif comment_level == 2:
            comment = SecondLevelComment.objects.filter(comment_id=comment_id).first()
        if user and comment:
            liked = comment.liked_by_users.filter(user_id=user.user_id).first()
            # 取消点赞
            if liked:
                comment.like_count -= 1
                comment.liked_by_users.remove(user)
                comment.save()
                return JsonResponse({'message': '取消点赞成功', 'is_success': True})
            # 点赞
            else:
                comment.like_count += 1
                comment.liked_by_users.add(user)
                comment.save()
                # 被点赞的评论的作者收到通知
                notification = Notification(user_id=comment.user_id, title='你被赞了！')
                paper = comment.paper_id
                paper_title = paper.title
                notification.content = '你在论文《' + paper_title + '》的评论被用户' + user.username + '点赞了！'
                notification.save()
                return JsonResponse({'message': '点赞成功', 'is_success': True})
        else:
            return JsonResponse({'error': '用户或评论不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def batch_download_papers(request):
    """
    批量下载文献
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.session.get('username')
        paper_ids = data.get('paper_id_list')
        user = User.objects.filter(username=username).first()
        papers = Paper.objects.filter(paper_id__in=paper_ids)
        if user and papers:
            for paper in papers:
                # 首先判断文献是否有本地副本，没有则下载到服务器
                if not paper.local_path or not os.path.exists(paper.local_path):
                    original_url = paper.original_url
                    # 将路径中的abs修改为pdf，最后加上.pdf后缀
                    original_url = original_url.replace('abs', 'pdf') + '.pdf'
                    # 访问url，下载文献到服务器
                    filename = str(paper.paper_id)
                    local_path = downloadPaper(original_url, filename)
                    paper.local_path = local_path
                    paper.save()

            # 将所有paper打包成zip文件，存入BATCH_DOWNLOAD_PATH，返回zip文件路径
            zip_name = (username + '_batchDownload_' + time.strftime('%Y%m%d%H%M%S') +
                        '_%d' % random.randint(0, 100) + '.zip')
            zip_file_path = os.path.join(BATCH_DOWNLOAD_PATH, zip_name)
            print(zip_file_path)
            with zipfile.ZipFile(zip_file_path, 'w') as z:
                for paper in papers:
                    z.write(paper.local_path, paper.title + '.pdf')
            zip_url = BATCH_DOWNLOAD_URL + zip_name
            return JsonResponse({'message': '下载成功', 'zip_url': zip_url, 'is_success': True})
        else:
            return JsonResponse({'error': '用户或文献不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def get_paper_info(request):
    """
    获取文献信息
    """
    if request.method == 'GET':
        paper_id = request.GET.get('paper_id')
        paper = Paper.objects.filter(paper_id=paper_id).first()
        if paper:
            return JsonResponse({'message': '获取成功',
                                 'paper_id': paper.paper_id,
                                 'title': paper.title,
                                 'authors': paper.authors,
                                 'abstract': paper.abstract,
                                 'publication_date': paper.publication_date.strftime("%Y-%m-%d"),
                                 'journal': paper.journal,
                                 'citation_count': paper.citation_count,
                                 'read_count': paper.read_count,
                                 'like_count': paper.like_count,
                                 'collect_count': paper.collect_count,
                                 'download_count': paper.download_count,
                                 'comment_count': paper.comment_count,
                                 'score': paper.score,
                                 'score_count': paper.score_count,
                                 'original_url': paper.original_url,
                                 'is_success': True})
        else:
            return JsonResponse({'error': '文献不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def get_user_paper_info(request):
    """
    获得用户对论文的收藏、点赞、评分情况
    """
    if request.method == 'GET':
        username = request.session.get('username')
        paper_id = request.GET.get('paper_id')
        user = User.objects.filter(username=username).first()
        paper = Paper.objects.filter(paper_id=paper_id).first()
        if user and paper:
            liked = user.liked_papers.filter(paper_id=paper_id).first()
            collected = user.collected_papers.filter(paper_id=paper_id).first()
            scored = PaperScore.objects.filter(user_id=user, paper_id=paper).first()
            return JsonResponse({'message': '获取成功',
                                 'liked': True if liked else False,
                                 'collected': True if collected else False,
                                 'scored': True if scored else False,
                                 'score': scored.score if scored else 0,
                                 'is_success': True})
        else:
            return JsonResponse({'error': '用户或文献不存在', 'is_success': False}, status=400)


@require_http_methods('POST')
def save_paper_note(request):
    '''
    保存用户的笔记和批注
    '''
    data = json.loads(request.body)
    params = data.get('params')

    x = params.get('x')
    y = params.get('y')
    width = params.get('width')
    height = params.get('height')
    pageNum = params.get('pageNum')
    comment = params.get('comment')
    paper_id = params.get('paper_id')
    isPublic = params.get('isPublic')
    username = request.session.get('username')

    user = User.objects.filter(username=username).first()

    paper = Paper.objects.filter(paper_id=paper_id).first()

    note = FileNote(user_id=user, paper_id=paper, x=x, y=y, width=width, height=height, pageNum=pageNum,
                    comment=comment, username=username, isPublic=isPublic)
    note.save()

    # 启动自动审核程序
    if_success, status_code, labels, reason = auto_comment_detection(comment)

    if if_success:
        auto_record = AutoNoteCheckRecord(note=note, labels=labels, reason=reason)
        auto_record.save()

        safe = True
        if len(labels) == 0 or labels.isspace():
            note.visibility = True
            auto_record.security = True
            note.save()
            auto_record.save()
        else:
            # 将不安全审核记录到表中
            safe = False
            risk_record = AutoNoteRiskRecord(check_record=auto_record)
            risk_record.save()
            return reply.fail(msg='存在非绿色内容')

    if isPublic:
        # 将笔记公开
        annotation = FileAnnotation(note=note, user_id=user, paper_id=paper)
        annotation.save()

    data = {
        'x': x,
        'y': y,
        'width': width,
        'height': height,
        'pageNum': pageNum,
        'comment': comment,
        'userName': username,
        'isPublic': isPublic,
        'id': note.note_id
    }

    return reply.success(data=data, msg="成功保存笔记或批注")


@require_http_methods("GET")
def get_paper_annotation(request):
    '''
    获得公开批注
    '''
    paper_id = request.GET.get('paper_id')
    print(paper_id)

    data = {
        'annotations': []
    }

    paper = Paper.objects.filter(paper_id=paper_id).first()

    print(paper)

    annotation_list = FileAnnotation.objects.filter(paper_id=paper, visibility=True)

    print(annotation_list)

    for annotation in annotation_list:
        note = annotation.note
        x = note.x
        y = note.y
        width = note.width
        height = note.height
        pageNum = note.pageNum
        comment = note.comment
        username = note.username
        isPublic = note.isPublic
        id = note.note_id
        date = note.date
        data['annotations'].append({
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'pageNum': pageNum,
            'comment': comment,
            'userName': username,
            'isPublic': isPublic,
            'id': id,               # id为note_id
            'date': date
        })

    username = request.session.get('username')
    note_list = FileNote.objects.filter(paper_id=paper, username=username,  isPublic=False)
    for note in note_list:
        x = note.x
        y = note.y
        width = note.width
        height = note.height
        pageNum = note.pageNum
        comment = note.comment
        isPublic = note.isPublic
        id = note.note_id
        date = note.date
        data['annotations'].append({
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'pageNum': pageNum,
            'comment': comment,
            'userName': username,
            'isPublic': isPublic,
            'id': id,               # id为note_id
            'date': date
        })

    return reply.success(data=data, msg="成功获取批注")


@require_http_methods('POST')
def delete_paper_note(request):
    '''
    删除笔记（对应的批注也被删除）
    '''
    data = json.loads(request.body)
    note_id = data.get('annotation_id') # 由于后端提供的是note_id，前端返回的也是note_id

    note = FileNote.objects.filter(note_id=note_id).first()

    if not note:
        return reply.fail(
            data={
                'type': "fail"
            },
            msg="未查询到该笔记记录"
        )

    note.delete()
    return reply.success(
        data={
            'type': "success"
        },
        msg="删除笔记成功"
    )


@require_http_methods('POST')
def report_paper_annotation(request):
    '''
    举报批注
    '''
    data = json.loads(request.body)
    print(data)
    username = request.session.get('username')
    note_id = data.get('annotation_id')
    reason = data.get('reason')
    print(reason)
    user = User.objects.filter(username=username).first()

    note = FileNote.objects.filter(note_id=note_id).first()
    annotation = FileAnnotation.objects.filter(note=note).first()

    report = AnnotationReport(annotation=annotation, user=user, content=reason)
    report.save()

    data = {
        'type': 'success'
    }

    return reply.success(data=data, msg="举报成功，请等待人工审核结果")


@require_http_methods('POST')
def save_document_note(request):
    '''
    保存用户的笔记
    '''
    data = json.loads(request.body)
    params = data.get('params')
    x = params.get('x')
    y = params.get('y')
    width = params.get('width')
    height = params.get('height')
    pageNum = params.get('pageNum')
    comment = params.get('comment')
    paper_id = params.get('paper_id')
    username = request.session.get('username')

    user = User.objects.filter(username=username).first()

    document = UserDocument.objects.filter(document_id=paper_id).first()

    note = DocumentNote(user=user, document=document, x=x, y=y, width=width, height=height, pageNum=pageNum,
                    comment=comment, username=username)
    note.save()

    data = {
        'x': x,
        'y': y,
        'width': width,
        'height': height,
        'pageNum': pageNum,
        'comment': comment,
        'userName': username,
        'isPublic': True,
        'id': note.note_id
    }

    return reply.success(data=data, msg="成功保存笔记")


@require_http_methods("GET")
def get_document_note(request):
    '''
    获得笔记
    '''
    document_id = request.GET.get('document_id')

    data = {
        'annotations': []
    }

    document = UserDocument.objects.filter(document_id=document_id).first()

    note_list = DocumentNote.objects.filter(document=document)

    for note in note_list:
        x = note.x
        y = note.y
        width = note.width
        height = note.height
        pageNum = note.pageNum
        comment = note.comment
        username = note.username
        id = note.note_id
        date = note.date
        data['annotations'].append({
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'pageNum': pageNum,
            'comment': comment,
            'userName': username,
            'isPublic': True,
            'id': id,
            'date': date
        })

    return reply.success(data=data, msg="成功获取笔记")


@require_http_methods('POST')
def delete_document_note(request):
    '''
    删除笔记
    '''
    data = json.loads(request.body)
    note_id = data.get('annotation_id')

    note = DocumentNote.objects.filter(note_id=note_id).first()

    if not note:
        return reply.fail(
            data={
                'type': "fail"
            },
            msg="未查询到该笔记记录"
        )

    note.delete()
    return reply.success(
        data={
            'type': "success"
        },
        msg="删除笔记成功"
    )


@require_http_methods("GET")
def translate_abstract(require):
    paper_id = require.GET.get('paper_id')

    paper = Paper.objects.filter(paper_id=paper_id).first()

    if paper is None:
        return reply.fail(msg="未找到该论文")

    abstract = paper.abstract

    translated_abstract = text_translate_tool(abstract)

    data = {
        "translatedSummary": translated_abstract[0],
    }

    print("data:" + str(data))

    return reply.success(data=data, msg="成功获取摘要翻译结果")


@require_http_methods('GET')
def download_paper_translated_url(request):
    '''
    下载用户上传文档的翻译结果(pdf文件)
    '''
    document_id = request.GET.get('document_id')
    paper_path = Paper.objects.filter(paper_id=document_id).values('local_path').first().values()
    paper_name = Paper.objects.filter(paper_id=document_id).first()
    value_list = list(paper_path)
    path = value_list[0]  # pdf的path
    # print(document_name)
    username = request.session.get('username')

    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.abspath(os.path.join(script_dir, '../../' + path))
    print("pdf_path:" + pdf_path)
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                print(text)
    except FileNotFoundError:
        print(f"文件 {pdf_path} 不存在。")
    except Exception as e:
        print(f"读取 PDF 文件时发生错误: {str(e)}")
    if pdf_path:
        # 对该论文进行翻译
        if (pdf_translate(pdf_path=pdf_path, pdf_name=paper_name)):
            if not isinstance(paper_name, str):
                paper_name = str(paper_name)
            translated_filename = os.path.abspath(os.path.join(script_dir, '../../' + 'scripts/translated_pdf',
                                                               'translated__' + paper_name + '.pdf'))
        else:
            data = {
                'zip_url': '/',
                'is_success': False
            }
            return reply.fail(data=data, msg="没翻译成功")
        # print(os.path.join(script_dir, '../../' + 'scripts/translated_pdf',
        #                                                        'translated__' + paper_name.title + '.pdf'))

        # 将所有paper打包成zip文件，存入BATCH_DOWNLOAD_PATH，返回zip文件路径
        zip_name = (username + '_batchDownload_' + time.strftime('%Y%m%d%H%M%S') +
                    '_%d' % random.randint(0, 100) + '.zip')
        zip_file_path = os.path.join(BATCH_DOWNLOAD_PATH, zip_name)
        print(zip_file_path)
        with zipfile.ZipFile(zip_file_path, 'w') as z:
            z.write(translated_filename, arcname=os.path.basename(translated_filename))

        zip_url = BATCH_DOWNLOAD_URL + zip_name

        data = {
            'zip_url': zip_url,
            'is_success': True
        }
        return reply.success(data=data, msg="成功翻译并下载翻译结果")

    else:
        data = {
            'zip_url': '/',
            'is_success': False
        }
        return reply.fail(data=data, msg="找不到需要翻译的论文")
