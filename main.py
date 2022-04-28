import subprocess
import sys
import os
import time
import rich
import random
import shutil
import stat
import signal
import telegram
import requests
import ffmpeg
import PIL
import glob

from rich import print
from rich import box
from rich.console import Console
from rich.columns import Columns
from rich.table import Table
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from get import DC_CON
from PIL import Image, ImageSequence
from PIL import features
from pathlib import Path
from emoji import Emoji

console = Console()
dccon = DC_CON()

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
    try:
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
        
        download_pwd = pwd+"/"+data_selected
        
        if os.path.exists(download_pwd):
            shutil.rmtree(download_pwd)
        os.makedirs(download_pwd)
        
        i=0
        for download_list in cdn_image_list:
            context.bot.edit_message_text(text=str(i+1)+"/"+str(len(cdn_image_list))+" 다운로드 진행 중...\n"+progress(i+1,len(cdn_image_list)),
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id)
            download(download_list[1],download_pwd+"/"+str(i)+"."+download_list[0])
            i = i + 1
        
        i=0
        files = glob.glob(download_pwd+'/*')
        for f in files:
            context.bot.edit_message_text(text=str(i+1)+"/"+str(len(cdn_image_list))+" 파일 변환 진행 중...\n"+progress(i+1,len(cdn_image_list)),
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id)
            title, ext = os.path.splitext(f)
            if ext in ['.gif']:
                ConvertWEBP(f)
                os.remove(f)
                time.sleep(0.5)
            if ext in ['.jpg', '.png']:
                img = Image.open(f).convert('RGB')
                img_resize = img.resize((int(512), int(512)))
                img_resize.save(title + '_resize' + ".png","png",quality=70)
                os.remove(f)
                os.rename(title + '_resize' + ".png",f)
            i=i+1
            

        i=0
        check_first = True
        files = glob.glob(download_pwd+'/*')
        
        try:
            context.bot.get_sticker_set("A"+data_selected+"_by_dcon_get_bot") #등록되지 않았다면 Exception 발생->True
            check_first = False #등록된 스티커라면 False로 변경
            set_sticker = context.bot.get_sticker_set("A"+data_selected+"_by_dcon_get_bot").stickers
            for tmp_sticker in set_sticker:
                context.bot.edit_message_text(text=str(i+1)+"/"+str(len(set_sticker))+" 중복된 데이터를 정리하고 있습니다...\n"+progress(i+1,len(set_sticker)),
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id)
                succ = context.bot.delete_sticker_from_set(tmp_sticker.file_id)
                i=i+1
        except:
            check_first = True
            console.log("check_first = "+str(check_first))
        
        i=0
        for f in files:
            try:
                context.bot.edit_message_text(text=str(i+1)+"/"+str(len(cdn_image_list))+" 파일 업로드 진행 중...\n"+progress(i+1,len(cdn_image_list)),
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id)
                title, ext = os.path.splitext(f)
                console.log("Processing "+title+ext)
                if ext in ['.jpg', '.png']: #정적스티커
                    if check_first: #첫 등록인경우
                        context.bot.create_new_sticker_set(user_id=str(update.callback_query.from_user.id),name="A"+data_selected+"_by_dcon_get_bot",title=update.callback_query.data.split("|")[1],png_sticker=open(f, 'rb'),emojis=Emoji.random_emoji())
                        check_first=False #첫 등록이후, 등록된 스티커패키지가 있음으로 변경(check_first->False)
                    elif not check_first: #등록내용이 있는경우
                        context.bot.add_sticker_to_set(user_id=str(update.callback_query.from_user.id),name="A"+data_selected+"_by_dcon_get_bot",png_sticker=open(f, 'rb'),emojis=Emoji.random_emoji())
                if ext in ['.webm','.WEBM','.webp']: #동적스티커
                    if check_first: #첫 등록인경우
                        context.bot.create_new_sticker_set(user_id=str(update.callback_query.from_user.id),name="A"+data_selected+"_by_dcon_get_bot",title=update.callback_query.data.split("|")[1],webm_sticker=open(f, 'rb'),emojis=Emoji.random_emoji())
                        check_first=False #첫 등록이후, 등록된 스티커패키지가 있음으로 변경(check_first->False)
                    elif not check_first: #등록내용이 있는경우
                        context.bot.add_sticker_to_set(user_id=str(update.callback_query.from_user.id),name="A"+data_selected+"_by_dcon_get_bot",webm_sticker=open(f, 'rb'),emojis=Emoji.random_emoji())
                i = i+1
            except Exception as e:
                console.log("[bold][red]ERROR[/bold][/red] " +str(e.message))
                context.bot.edit_message_text(text="[ERROR] 텔레그램 서버가 응답하지 않습니다. 잠시 후 재시도 해 주세요.",
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id)
                return 0
                
        context.bot.edit_message_text(text="https://t.me/addstickers/"+"A"+data_selected+"_by_dcon_get_bot",
                                            chat_id=update.callback_query.message.chat_id,
                                            message_id=update.callback_query.message.message_id)
        shutil.rmtree(download_pwd)
        console.log(data_selected+" 등록완료")
    except Exception as ex:
        console.log("[bold][red]ERROR[/bold][/red] " +str(ex))
        context.bot.edit_message_text(text="[ERROR] 처리되지 않은 오류가 발생하였습니다.\nException > "+str(ex),
                                    chat_id=update.callback_query.message.chat_id,
                                    message_id=update.callback_query.message.message_id)
    
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
    bar_len = 15
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '■' * filled_len + '□' * (bar_len - filled_len)

    retdata = ('🖨️ [%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    return retdata;
    
def download(url, file_name):
    with open(file_name, "wb") as file:   # open in binary mode
        response = requests.get(url)               # get request
        file.write(response.content)      # write to file

def random_emoji():
    n = ['😀', '😁', '🤣', '😃', '😄', '😅', '😆', '😉', '😊', '😋', '😎', '😍', '😘', '😗']
    random.shuffle(n)
    text = n[0]
    return text
    
def ConvertWEBP(filepath):
    p = Path(filepath)
    in_file = ffmpeg.input(filepath)
    in_info = ffmpeg.probe(filepath)
    stream = in_info['streams'][0]
    fmt = in_info['format']
    in_file = in_file.filter('fps', fps=30)
    if stream['width'] >= stream['height']:
        in_file = in_file.filter('scale', 512, -1)
    else:
        in_file = in_file.filter('scale', -1, 512)
    if 'duration' in fmt:
        duration = float(fmt['duration'])
        if duration > 3.0:
                in_file = in_file.filter('setpts', f"(3.0/{duration})*PTS")
    else:
        in_file = in_file.filter('setpts', f"1.0*PTS")
    out_path = str(p.with_suffix('.WEBM'))
    if os.path.exists(out_path):
        out_path = str(p.with_suffix('.telegram.WEBM'))
    in_file.output(
                out_path,
                pix_fmt='yuv420p',
                vcodec='libvpx-vp9',
                fs='255KB',
                crf='60',
                an=None,  # Remove Audio
                loglevel="error",
            ).overwrite_output().run()
            
if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    try:
        telegram_bot_init()
    except Exception as ex:
        #console.log(ex)
        console.log("[bold][red][Important][/red][/bold] 처리되지 않은 오류가 발생했습니다.")
        exit(0)
        