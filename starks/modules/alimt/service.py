import logging
import json

from envcfg.raw import starks as config

from aliyunsdkcore.client import AcsClient
from aliyunsdkalimt.request.v20181012 import TranslateGeneralRequest


client = AcsClient(
    config.ALIYUN_ACCESS_KEY,
    config.ALIYUN_SECRET_KEY,
    "cn-hangzhou",
)


def zh2en(text):
    request = TranslateGeneralRequest.TranslateGeneralRequest()
    request.set_SourceLanguage("zh")
    request.set_SourceText(text)
    request.set_FormatType("text")
    request.set_TargetLanguage("en")
    request.set_method("POST")
    response = client.do_action_with_exception(request)
    data = json.loads(response)
    if data.get("Code") == "200":
        return data["Data"]["Translated"]
    else:
        logging.warn("Failed to translate")
        return None
