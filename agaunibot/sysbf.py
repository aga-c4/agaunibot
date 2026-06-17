import logging
import datetime
# import resource
from importlib import import_module

class SysBf:

    @staticmethod
    def get_max_memory_usage():
        max_memory = 0 # resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return max_memory

    @staticmethod
    def get_substring(text:str, start_text:str="", end_text:str=""):
        if start_text == "":
            start_index = 0
        else:
            start_index = text.find(start_text)   
        
        if end_text == "":
            end_index = len(text)
        else:
            end_index = text.find(end_text)

        if start_index == -1 or end_index == -1:
            return ""        
        
        return text[start_index + len(start_text):end_index]
    
    @staticmethod
    def class_factory(module_name, class_name, *args, **kwargs):
        logging.info(f"SysBF:Factory:New: {class_name} from {module_name}") 
        try:
            module = import_module(module_name)
            try:
                class_obj = getattr(module, class_name)
                try:
                    instance = class_obj(*args, **kwargs)
                    return instance  # Вы создали экземпляр класса.
                except:
                    logging.warning(f"Error new [{class_name}] in {class_obj.__class__.__name__}")        
            except:
                logging.warning(f"Error getattr [{class_name}]")        
        except Exception as e:
            logging.warning(f"Error import_module [{module_name}]:", e) 
        
        return None
    
    @staticmethod
    def call_method_fr_obj(obj, method_name, *args, **kwargs):
        # Получаем метод из объекта по имени
        method = getattr(obj, method_name, None)
        if callable(method):
            # Вызываем метод с переданными аргументами
            return method(*args, **kwargs)
        else:
            logging.warning(f"Method not found: {method_name} in {obj.__class__.__name__}")
            return None
            
    @staticmethod
    def merge_dicts(dict1, dict2):
        """Рекурсивно объединяет два словаря."""
        merged = dict1.copy()  # Копируем первый словарь

        for key, value in dict2.items():
            if key in merged:
                # Если значение - словарь, вызываем рекурсивно
                if isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = SysBf.merge_dicts(merged[key], value)
                # Если значение - список, объединяем списки
                # elif isinstance(merged[key], list) and isinstance(value, list):
                #     merged[key] = list(set(merged[key]) | set(value))  # Объединяем списки без дубликатов
                else:
                    # В противном случае заменяем значение
                    merged[key] = value
            else:
                # Если ключа нет в первом словаре, просто добавляем его
                merged[key] = value

        return merged
    
    @staticmethod
    def merge_lists(list1, list2):
        """Рекурсивно объединяет два списка."""
        merged = list1.copy()  # Копируем первый список

        for item in list2:
            if item not in merged:  # Добавляем только уникальные элементы
                merged.append(item)

        return merged

    @staticmethod
    def getitem(source, item, default=None):
        if type(source) is list:
            item_int = int(item)
            if len(source)>item_int:
                return source[item_int]
        elif type(source) is dict:
            return source.get(item, default)     
        return default    

    @staticmethod    
    def tzdt_fr_str(dt_str:str='', tz_str:str='') -> datetime:
        "Сначала пробуем 3 топовых формата, потом более медленно распознаем все. Если не определилось, то отдаст начало эпохи Unix"
        
        # https://pythonist.ru/preobrazovanie-strok-v-datu-so-vremenem/?ysclid=m17h82ndn110307520
        date_time_obj = datetime.datetime.fromtimestamp(0)
        if dt_str!='':
            try:
                date_time_obj = datetime.datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S.%f')
            except:
                try:
                    date_time_obj = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f')
                except:
                    try:
                        date_time_obj = datetime.datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S')
                    except:
                        try:
                            date_time_obj = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                        except:
                            try:
                                date_time_obj = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H')
                            except:
                                try:
                                    date_time_obj = datetime.datetime.strptime(dt_str, '%Y-%m-%d')
                                except:
                                    try:
                                        date_time_obj = datetime.datetime.strptime(dt_str, '%Y-%m')
                                    except:
                                        try:
                                            date_time_obj = parse(dt_str)
                                        except:
                                            logging.error(f'SysBf:tzdt_fr_str: Date format error [{dt_str}] type:' + str(type(dt_str)))
        return SysBf.tzdt(dt=date_time_obj, tz_str=tz_str)
    
    @staticmethod
    def tzdt(dt:datetime, tz_str:str='') -> datetime:
        if dt is None:
            return None
        if dt.tzinfo == tz_str:
            return dt
        if not dt.tzinfo is None:
            return SysBf.dt_to_tz(dt, tz_str)
        tzdt = dt
        if tz_str!='':
            try:
                timezone = pytz.timezone(tz_str)
                tzdt = timezone.localize(tzdt)
            except:
                logging.error(f'SysBf:tzdt: Timezone format error [{tz_str}] type:' + str(type(tz_str)) + ' time: ' + str(dt) + ' time_tipe:' + str(type(dt)))    

        return tzdt

    @staticmethod
    def dt_to_tz(dt:datetime, tz_str:str='') -> datetime:
        '''tz_str - пустая строка - возвращаем dt, notz - удаляем таймзону, оставляем текущее время'''
        if dt is None:
            return None
        if dt.tzinfo == tz_str:
            return dt
        if tz_str=='notz':
            return dt.replace(tzinfo=None)
        elif tz_str!='':
            timezone = pytz.timezone(tz_str)
            return  dt.astimezone(timezone)  
        return dt      
    