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
import glob
from get import DC_CON
import telegram
import requests

from rich import print
from rich import box
from rich.console import Console
from rich.columns import Columns
from rich.table import Table
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from PIL import Image, ImageSequence
from PIL import features
import moviepy.editor as mp
console = Console()
dccon = DC_CON()

def main():
    return 0

def telegram_bot_init():
    #https://python-telegram-bot.readthedocs.io/
    
    f = open("key", 'r')
    token = f.readlines()[0]
    f.close()
    
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
        
    start_handler = CommandHandler('start', telegram_start)
    dispatcher.add_handler(start_handler)
    search_handler = CommandHandler('search', telegram_search)
    dispatcher.add_handler(search_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_get))
    
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
    list_data = dccon.getList(keyword) #데이터 검색
    if list_data == "ERROR":
        context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text="검색된 내용이 없습니다.") #안내메세지 전송
        return 0
    show_list = []
    for data in list_data:
        show_list.append(InlineKeyboardButton(list_data[data][1], callback_data=data+"|"+list_data[data][1]))
    show_list.append(InlineKeyboardButton("취소", callback_data="cancel"))
    show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list)))
    update.message.reply_text("원하는 내용을 선택하세요", reply_markup=show_markup)
    return 0

def callback_get(update, context):
    data_selected = update.callback_query.data.split("|")[0]
    if data_selected.find("cancel") != -1 :
        context.bot.edit_message_text(text="취소하였습니다.",
                                      chat_id=update.callback_query.message.chat_id,
                                      message_id=update.callback_query.message.message_id)
        return
    context.bot.edit_message_text(text="다운로드를 준비하고 있습니다.",
                                      chat_id=update.callback_query.message.chat_id,
                                      message_id=update.callback_query.message.message_id)
    
    cdn_image_list = dccon.getImageCDN(data_selected)
    pwd = os.getcwd()
    os.makedirs(pwd+"\\"+data_selected)
    download_pwd = pwd+"\\"+data_selected
    
    i=0
    for download_list in cdn_image_list:
        context.bot.edit_message_text(text=str(i+1)+"/"+str(len(cdn_image_list))+" 다운로드 진행 중...\n"+progress(i+1,len(cdn_image_list)),
                                      chat_id=update.callback_query.message.chat_id,
                                      message_id=update.callback_query.message.message_id)
        download(download_list[1],download_pwd+"\\"+str(i)+"."+download_list[0])
        i = i + 1
    
    i=0
    files = glob.glob(download_pwd+'\\*')
    for f in files:
        context.bot.edit_message_text(text=str(i+1)+"/"+str(len(cdn_image_list))+" 파일 변환 진행 중...\n"+progress(i+1,len(cdn_image_list)),
                                      chat_id=update.callback_query.message.chat_id,
                                      message_id=update.callback_query.message.message_id)
        title, ext = os.path.splitext(f)
        if ext in ['.jpg', '.png']:
            img = Image.open(f).convert('RGB')
            img_resize = img.resize((int(512), int(512)))
            img_resize.save(title + '_resize' + ".png","png",quality=70)
            os.remove(f)
            os.rename(title + '_resize' + ".png",f)
        if ext in ['.gif']:
            #clip = mp.VideoFileClip(f).set_duration(2.9).resize((512,512)).without_audio()
            #clip.write_videofile(title + '_resize' + ".WEBM",fps=30,codec="vp9")
            os.remove(f)
        i=i+1
        

    i=0
    first = False
    files = glob.glob(download_pwd+'\\*')
    for f in files:
        try:
            context.bot.edit_message_text(text=str(i+1)+"/"+str(len(cdn_image_list))+" 파일 업로드 진행 중...\n"+progress(i+1,len(cdn_image_list)),
                                      chat_id=update.callback_query.message.chat_id,
                                      message_id=update.callback_query.message.message_id)
            title, ext = os.path.splitext(f)
            if ext in ['.jpg', '.png']:
                if not first: #첫 등록인경우
                    context.bot.create_new_sticker_set(user_id=str(update.callback_query.from_user.id),name="A"+data_selected+"_by_dcon_get_bot",title=update.callback_query.data.split("|")[1],png_sticker=open(f, 'rb'),emojis="👩")
                    first = True
                elif first: #등록내용이 있는경우
                    context.bot.add_sticker_to_set(user_id=str(update.callback_query.from_user.id),name="A"+data_selected+"_by_dcon_get_bot",png_sticker=open(f, 'rb'),emojis="👩")
            i = i+1
        except Exception as e:
            console.log("ERROR "+e)
            
    context.bot.edit_message_text(text="https://t.me/addstickers/"+"A"+data_selected+"_by_dcon_get_bot",
                                        chat_id=update.callback_query.message.chat_id,
                                        message_id=update.callback_query.message.message_id)
    shutil.rmtree(download_pwd)
    console.log(data_selected+" 등록완료")
    
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu
    
def telegram_start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="/search 키워드")
    return 0    
    
def sigint_handler(signal, frame):
    sys.exit(0)

def progress(count, total, suffix=''):
    bar_len = 20
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '■' * filled_len + '□' * (bar_len - filled_len)

    retdata = ('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    return retdata;
    
def download(url, file_name):
    with open(file_name, "wb") as file:   # open in binary mode
        response = requests.get(url)               # get request
        file.write(response.content)      # write to file
        
if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    try:
        telegram_bot_init()
        main()
    except Exception as ex:
        console.log(ex)
        console.log("[bold][red][Important][/red][/bold] 처리되지 않은 오류가 발생했습니다.")
        exit(0)