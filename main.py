import subprocess
import sys
import os
import time
import base64
import hashlib
import hmac
import rich
import random
import shutil
import stat
import signal
from get import DC_CON
import telegram

from rich import print
from rich import box
from rich.console import Console
from rich.columns import Columns
from rich.table import Table
console = Console()
dccon = DC_CON()

def main():
    console.log(dccon.getList("광대콘"))
    console.log(dccon.getImageCDN("17221"))
    return 0

def telegram_bot_init():
    #https://python-telegram-bot.readthedocs.io/
    updater = Updater(token='TOKEN', use_context=True)
    dispatcher = updater.dispatcher
        
    start_handler = CommandHandler('start', telegram_start)
    dispatcher.add_handler(start_handler)
    search_handler = CommandHandler('search', telegram_search)
    dispatcher.add_handler(search_handler)
    get_handler = CommandHandler('get', telegram_get)
    dispatcher.add_handler(get_handler)
    
    updater.start_polling()
    console.log(dispatcher.bot.get_me())
    console.log("Start Complete!")
    updater.idle()
    console.log(e)
    return 0

def telegram_get(update, context):
    return 0

def telegram_search(update, context):
    keyword = ' '.join(context.args).upper()
    if keyword == '':                   #인수가 없다면
        context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text="/search 키워드") #안내메세지 전송
        return 0
    list_data = dccon.getList(keyword)
    if list_data == "ERROR":
        context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text="검색된 내용이 없습니다.") #안내메세지 전송
        return 0
    context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id,
    reply_markup= telegram.InlineKeyboardMarkup(inline_keyboard=[[telegram.InlineKeyboardButton("버튼")]]))    
    return 0
    
def telegram_start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="/search 키워드")
    return 0    
    
def sigint_handler(signal, frame):
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    try:
        telegram_bot_init()
        main()
    except Exception as ex:
        console.log(ex)
        console.log("[bold][red][Important][/red][/bold] 처리되지 않은 오류가 발생했습니다.")
        exit(0)