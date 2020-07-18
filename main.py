import os
import datetime
import re

from bs4 import BeautifulSoup
import jpholiday
from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage
import requests

KABUTEC_GC_URL = "https://www.kabutec.jp/contents/compare/com.php?col1=8&scol1=0&col2=26&scol2=0&col3=27&scol3=0&market=0"


def get_today_list():
    """
    株テクからGC銘柄を取得する。
    """
    res = requests.get(KABUTEC_GC_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    li = soup.find_all(href=re.compile("kabutec.jp/company/fs_"))
    company_list = list(map(lambda item: item.contents[0], li))
    return company_list


def get_weekday():
    """
    平日の判定を行う。

    Returns
    -------
    ret : boolean
        True : 平日
        False : 休日
    """
    dt_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    if dt_jst.weekday() == 5 or dt_jst.weekday() == 6:
        ret = False
    else:
        if jpholiday.is_holiday(dt_jst.date()):
            ret = False
        else:
            ret = True
    return ret


if __name__ == "__main__":
    if get_weekday():
        li = get_today_list()
        line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
        msg = "本日のGC銘柄は{num}銘柄です。\n{li}".format(num=len(li), li="\n".join(li))
        print(msg)
        messages = TextSendMessage(text=msg)
        try:
            line_bot_api.broadcast(messages=messages)
        except LineBotApiError:
            pass
    else:
        print("今日は休みです。")
