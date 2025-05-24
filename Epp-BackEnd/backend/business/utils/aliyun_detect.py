from alibabacloud_green20220302.client import Client
from alibabacloud_green20220302 import models
from alibabacloud_tea_openapi.models import Config
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_tea_util import models as util_models
import json
import uuid

from business.utils import reply

# 内容安全API(阿里绿网) 7.5r/万次
# 用来是检测评论的合法性的方法，在scripts/aliyun_test中进行测试
access_key_id='LTAI5tA1748XZkNXokKZ9xSe'
access_key_secret='3vONTV9YqT39jB8qTpKOHzgw6LswNe'

def auto_comment_detection(content:str):

    service_parameters = {
        'content': content,
        'dataId': str(uuid.uuid1())
    }

    if service_parameters.get("content") is None or len(service_parameters.get("content").strip()) == 0:
        print("text moderation content is empty")

    text_moderation_request = models.TextModerationRequest(
        # 文本检测service：内容安全控制台文本增强版规则配置的serviceCode，示例：chat_detection
        service = 'comment_detection',  # 公聊评论内容检测
        service_parameters = json.dumps(service_parameters)
    )

    config = Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        # 连接时超时时间，单位毫秒（ms）。
        connect_timeout=3000,
        # 读取时超时时间，单位毫秒（ms）。
        read_timeout=6000,
        # 接入区域和地址请根据实际情况修改。
        region_id='cn-shanghai',
        endpoint='green-cip.cn-shanghai.aliyuncs.com'
    )
    # 注意，此处实例化的client请尽可能重复使用，避免重复建立连接，提升检测性能。
    client = Client(config)

    # 创建RuntimeObject实例并设置运行参数。
    runtime = util_models.RuntimeOptions()
    runtime.read_timeout = 10000
    runtime.connect_timeout = 10000
    try:
        response = client.text_moderation_with_options(text_moderation_request, runtime)
        # 自动路由
        if UtilClient.equal_number(500, response.status_code) or not response or not response.body or 200 != response.body.code:
            # 服务端错误，区域切换到cn-beijing
            config.region_id = 'cn-beijing'
            config.endpoint = 'green-cip.cn-beijing.aliyuncs.com'
            client = Client(config)
            response = client.text_moderation_with_options(text_moderation_request, runtime)

        if response.status_code == 200:
            # 调用成功。
            # 获取审核结果。
            result = response.body
            # result说明(用于输出细化违规原因)
            """
            {
                "Code": 200,                                        # 状态码 200表示请求成功
                "Data": {
                    "Labels": "sexual_content",                     # 标签
                    "Reason": "{
                                  \"riskLevel\":\"high\",           # 风险等级
                                  \"riskTips\":\"色情_低俗词\",      # 细分标签
                                  \"riskWords\":\"色情服务\"}",      # 命中风险内容
                    "AccountId": "10123****"
                },
                "Message": "OK",
                "RequestId": "AAAAAA-BBBB-CCCCC-DDDD-EEEEEEEE****"
            }
            """
            print('response success. result:{}'.format(result))
            if result.code == 200:
                resultData = result.data
                print('labels:{}, reason:{}'.format(resultData.labels, resultData.reason))

                return True, response.status_code, resultData.labels, resultData.reason

        else:
            print('response not success. status:{} ,result:{}'.format(response.status_code, response))
            return False, response.status_code, None, None

    except Exception as err:
        print(err)