import telebot
from telebot import types # для указание типов
from telebot.util import quick_markup
import logging
from time import sleep

class Telegram:

    status = False
    bot = None
    parse_mode = 'HTML'

    def __init__(self, telegram_conf:dict):
        self.status = True
        telegram_api_token = telegram_conf.get('api_token', None)
        
        if telegram_api_token is None:
            self.status = False    
            
        if self.status:
            try:   
                self.bot = telebot.TeleBot(telegram_api_token)
                logging.warning("TeleBot is activated!")
            except:
                logging.warning("TeleBot init problems!")
                self.status = False

    def get_status(self):
        return self.status
    
    def set_status(self, status:bool):
        if status:
            self.status = True
        else:
            self.status = False    
    
    def send_message(self, channel:str, text, *, reply_markup=None) -> int:
        if not self.status:
            return 0  
        return self.bot.send_message(channel, text, disable_web_page_preview=True, parse_mode=self.parse_mode, reply_markup=self.prepare_markup(reply_markup)) 
    
    def send_photo(self, channel:str, img_buf=None, *, reply_markup=None) -> int:
        if not self.status:
            return 0  
        return self.bot.send_photo(channel, img_buf, reply_markup=self.prepare_markup(reply_markup))
    
    def send_document(self, channel:str, img_buf=None, *, reply_markup=None) -> int:
        if not self.status:
            return 0  
        return self.bot.send_document(channel, document=img_buf, reply_markup=self.prepare_markup(reply_markup))
    
    def download_file(self, file_id, filename:str=None):
        if filename is None or filename.strip()=="":
            return None
        else:
            file_info = self.bot.get_file(file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            with open(filename, 'wb') as new_file:
                new_file.write(downloaded_file)
            return filename        
    

    def edit_message_text(self, channel:str, message_id:str, *, new_text:str, reply_markup=None) -> int:
        if not self.status:
            return 0  
        return self.bot.edit_message_text(chat_id=channel, 
                                           message_id=message_id, 
                                           text=new_text, 
                                           reply_markup=self.prepare_markup(reply_markup))

        
    def edit_message_media(self, channel:str, message_id:str, *, img_buf=None, reply_markup=None) -> int:
        if not self.status:
            return 0  
        photo = types.InputMediaPhoto(img_buf)
        return self.bot.edit_message_media(chat_id=channel, 
                                           message_id=message_id, 
                                           media=photo, 
                                           reply_markup=self.prepare_markup(reply_markup))  
        

    def delete_message_text(self, channel:str, message_id:str) -> int:
        if not self.status:
            return 0  
        self.bot.delete_message(chat_id=channel, message_id=message_id)
        return 1


    def prepare_markup(self, reply_markup:dict=None):
        mktype_in = reply_markup.get("type", "InlineKeyboardMarkup")
        if mktype_in=="ReplyKeyboardMarku":
            mktype = "ReplyKeyboardMarku"
        else:
            mktype = "InlineKeyboardMarkup" 
        row_width = reply_markup.get("type", 3)    
        items_groups = reply_markup.get("items", [])
        if not type(items_groups)==list or len(items_groups)==0:
            return None
        else:      
            if mktype=="InlineKeyboardMarkup":   
                markup = types.InlineKeyboardMarkup(row_width=row_width)
                # Может быть список списков, а может быть одноуровневый
                for itemlist in items_groups:
                    if type(itemlist) is list:
                        if len(itemlist)>0:
                            add_list = []
                            for mkitem in itemlist:
                                if type(mkitem) is dict:
                                    add_list.append(types.InlineKeyboardButton(mkitem["text"], callback_data=mkitem["command"]))
                                else:
                                    add_list.append(types.InlineKeyboardButton(mkitem, callback_data=mkitem))    
                            markup.add(*add_list)    
                    else:
                        add_list = []
                        for mkitem in itemlist:
                            if type(mkitem) is dict:
                                add_list.append(types.InlineKeyboardButton(mkitem["text"], callback_data=mkitem["command"]))
                            else:
                                add_list.append(types.InlineKeyboardButton(mkitem, callback_data=mkitem))    
                        markup.add(*add_list) 
            elif mktype=="ReplyKeyboardMarkup":      
                # Здесь список одноуровневый с просто текстовыми элементами
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(*items_groups)
               
        return markup


    def get_user_info(self, user_id):
        user = self.bot.get_chat(user_id)  # Получаем информацию о пользователе
        user_info = {
            'first_name': user.first_name
        }
        if type(user.username) is str:
            user_info["username"] = user.username
        else:
            user_info["username"] = ""    
        return user_info

