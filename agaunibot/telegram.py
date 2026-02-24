import telebot
from telebot import types # для указание типов
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
                logging.info("TeleBot is activated!")
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
        if reply_markup is None:
            return None
        
        mktype_in = reply_markup.get("type", "InlineKeyboardMarkup")
        if mktype_in=="ReplyKeyboardMarkup":
            mktype = "ReplyKeyboardMarkup"
        else:
            mktype = "InlineKeyboardMarkup"    
        row_width = reply_markup.get("row_width", 3)    
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
                        add_list_all = []
                        if type(itemlist) is list:
                            add_list = []
                            for mkitem in itemlist:
                                if type(mkitem) is dict:
                                    add_list.append(types.InlineKeyboardButton(mkitem["text"], callback_data=mkitem["command"]))
                                else:
                                    add_list.append(types.InlineKeyboardButton(mkitem, callback_data=mkitem))
                                markup.add(*add_list)       
                        else:
                            if type(itemlist) is dict:
                                add_list_all.append(types.InlineKeyboardButton(itemlist["text"], callback_data=itemlist["command"]))
                            else:
                                add_list_all.append(types.InlineKeyboardButton(itemlist, callback_data=itemlist))
                        markup.add(*add_list_all)       
            elif mktype=="ReplyKeyboardMarkup":      
                # Здесь список одноуровневый с просто текстовыми элементами
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                add_list_all = []
                for itemlist in items_groups:
                    if type(itemlist) is list:
                        add_list = []
                        for mkitem in itemlist:
                            if type(mkitem) is str:
                                add_list.append(mkitem)   
                        markup.add(*add_list)
                    elif type(itemlist) is str:
                        add_list_all.append(itemlist)   
                    markup.add(*add_list_all)        
               
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
    
    
    def get_data_from_message(self, in_message):
        res = {
            "command": "",
            "command_obj": None,
            "command_info": None,
            "text": "",
            "data": "",
            "json": {},
            "from_user": {},
            "chat": {}
        }
        res["command"], res["command_obj"], res["command_info"] = self.get_dev_comm_by_str(in_message)

        if hasattr(in_message, "data"):
            res["data"] = in_message.data
        if hasattr(in_message, "text"):
            res["text"] = in_message.text  
        if hasattr(in_message, "json"):
            res["json"] = in_message.json      

        res["from_user"]={}
        if hasattr(in_message, "from_user"):
            if hasattr(in_message.from_user, "id"):
                res["from_user"]["id"] = in_message.from_user.id
            if hasattr(in_message.from_user, "id"):
                res["from_user"]["first_name"] = in_message.from_user.first_name
        
        res["chat"]={}
        if hasattr(in_message, "chat"):
            res["chat"]["id"] = in_message.chat.id
        
        return res
    
    
    def get_dev_comm_by_str(self, route_str:str=None): 
        command = ""
        obj = ""
        info = ""
        route_str_upd = route_str.strip()
        if route_str_upd != "":
            all_route_list = route_str_upd.split(':')
            if len(all_route_list)>1:
                command = all_route_list[1].strip()
            if len(all_route_list)>2:
                obj = all_route_list[2].strip()
            if len(all_route_list)>3:
                info = all_route_list[3]    

        return (command, obj, info)
    

    def bind_message_funct(self, botapp):

        @self.bot.message_handler(commands=['start'])
        def start(in_message):
            try:
                botapp.use_route(in_message=self.get_data_from_message(in_message), message_type="start")
            except Exception:
                logging.exception("Exeption in message_handler:commands:start:")     
                
        @self.bot.message_handler(content_types=['text'])
        def func(in_message):
            try:
                botapp.use_route(in_message=self.get_data_from_message(in_message), message_type="text")
            except Exception:
                logging.exception("Error in message_handler:content_types:text")             

        @self.bot.callback_query_handler()
        def callback_query(in_message):
            try:
                botapp.use_route(in_message=self.get_data_from_message(in_message), message_type="callback")
            except Exception:
                logging.exception("Error in callback_query_handler")    

        @self.bot.message_handler(content_types=['document'])
        def handle_docs_photo(in_message):
            try:
                botapp.use_route(in_message=self.get_data_from_message(in_message), message_type="document")
            except Exception:
                logging.exception("Error in message_handler:content_types:document")  

        while True:
            try:
                logging.info("Try to connect by Telebot")    
                self.bot.polling(none_stop=True)
            except Exception:
                logging.exception("Error in Telebot, reconnect in 60s")    
                self.bot.sleep(60)             

