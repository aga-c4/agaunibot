class InMessage:
    message_id = None
    command = ""
    command_obj = None
    command_info = None
    text = ""
    data = ""
    json = {}
    from_user = {"id": 0, "first_name":""}
    chat = {"id": 0}
    rotelist = []
    reply_markup = None
    
    def __init__(self, in_message):
        # TODO - Привязать к классу мессенджера 
        if hasattr(in_message, "data"):
            self.data = in_message.data
            self.command, self.command_obj, self.command_info = self.get_dev_comm_by_str(in_message.data)
            self.rotelist = self.get_controller_route_by_str(in_message.data)
        if hasattr(in_message, "text"):
            self.text = in_message.text  
        if hasattr(in_message, "json"):
            self.json = in_message.json  
            self.reply_markup = None
            reply_markup = in_message.json.get("message", {}).get("reply_markup", {}).get("inline_keyboard", None)  
            all_markup_list = []
            if type(reply_markup) is list:
                for grlist in reply_markup:
                    if type(grlist) is list:
                        markup_list = [] 
                        for item in grlist:
                            if type(item) is dict:
                                if item.get("text","")!="":
                                    markup_list.append({"text": item.get("text",""), "command": item.get("callback_data","")}) 
                            else:
                                markup_list.append(item)
                        if len(markup_list)>0:
                            all_markup_list.append(markup_list) 
            if len(all_markup_list)>0:
                print("all_markup_list:")
                print(all_markup_list)
                self.reply_markup = all_markup_list                 



        if hasattr(in_message, "message") and hasattr(in_message.message, "id"):     
            self.message_id = in_message.message.message_id     

        if hasattr(in_message, "from_user"):
            if hasattr(in_message.from_user, "id"):
                self.from_user["id"] = in_message.from_user.id
            if hasattr(in_message.from_user, "id"):
                self.from_user["first_name"] = in_message.from_user.first_name

        if hasattr(in_message, "chat"):
            self.chat["id"] = in_message.chat.id


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


    def get_controller_route_by_str(self, route_str:str=None)->list: 
        result = []
        if route_str != "":
            all_route_list = route_str.split(':')
            if len(all_route_list)>1:
                result = all_route_list[1:]    
        return result
    