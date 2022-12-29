from core.models import (
    Product, Chat, Intent, 
    LettersToNumber, ShoppingList, Similarity, WordSimilarity
)
from django.db import models
from random import choice, choices
from django.db.models import Q


def introduction_text():
        products = Product.objects.filter(exist=True)
        product_name_list = ''
        for product in products:
            product_name_list += f"\t{product.name} - {product.price}\n"            
        introduction_txt = f"سلام به سوپری ما خوش اومدی  من دستیار خریدت هستم\nاقلام موجود:\n{'-'*40}\n{product_name_list}{'-'*40}"
        return introduction_txt


def guide_text():
    guide_txt = 'هروقت خریدت تموم شد کافیه خداحافظی کنی\nقبلش هم میتونی لیست کل خرید هاتو بپرسی\nاینم بگم ما اینجا چیزی رو پس نمیگیریم!'
    return guide_txt


def request_handler(user_request, customer_id, previous_intent):
    # qs stand for queryset
    chat_qs = Chat.objects.annotate(
        match=WordSimilarity("request", models.Value(user_request))
    ).filter(
        Q(match__gt=0.4) , ~Q(intent="سلام و احوال پرسی"), ~Q(intent="درخواست قیمت کل"), ~Q(intent="خداحافظی و حساب کتاب")
    ).order_by("-match")
    
    chat_qs_sentence = Chat.objects.annotate(
        match=Similarity("request", models.Value(user_request))
    ).filter(
        Q(match__gt=0.4) , (Q(intent="سلام و احوال پرسی") | Q(intent="درخواست قیمت کل") | Q(intent="خداحافظی و حساب کتاب"))
    ).order_by("-match")  #0.2 is good
    
    lttrs_to_num_qs = LettersToNumber.objects.annotate(
        match=WordSimilarity("letters", models.Value(user_request))
    ).filter(match__gt=0.4).order_by("-match")
    
    product_qs = Product.objects.annotate(
        match=WordSimilarity("name", models.Value(user_request))
    ).filter(match__gt=0.4).order_by("-match")
    
    
    if product_qs.filter(exist=False):
        msg_list = ['نداریم متاسفانه', 'شرمنده نداریم', 'موجود نیست', 'برو از مغاره روبرویی بگیر', 'برو دوتا کوچه پایین تر اونجا داره']
        msg = choice(msg_list)
        result = f'{product_qs.filter(exist=False).first().name} {msg} '
        return result, (None, None), False
    
    
    if chat_qs:
        first_chat_obj = chat_qs.first()
        
        if lttrs_to_num_qs:
            if product_qs.filter(exist=True):
                        
                product = product_qs.filter(exist=True).first()
                count = lttrs_to_num_qs.first().number
              
                if first_chat_obj.intent.title == "درخواست جنس":
                    ShoppingList.objects.create(customer=customer_id, product=product, count=count)
                    msg_list = [msg.response for msg in Chat.objects.filter(intent="درخواست جنس و گفتن تعداد جنس")]
                    return choice(msg_list), (None, None), False
                            
                if first_chat_obj.intent.title == "سوال درباره موجود بودن جنس":
                    msg_list = ["بله هرچقدر {} بخای موجوده ", "اره داش هرچنتا {} بخای انبار هست", "بله جناب {} به تعداد موجوده", "اره {} به مقدار هست"]
                    return choice(msg_list).format(product.name), ("سوال درباره موجود بودن جنس", product), False
                
                if first_chat_obj.intent.title == "سوال درباره قیمت جنس":
                    return f"{product.name} {count} تاش میشه {product.price*count} تومن", ("سوال درباره قیمت جنس", product), False          
                  
                  
            else:
                count = lttrs_to_num_qs.first().number
                
                if first_chat_obj.intent.title == "درخواست جنس":
                    if (previous_intent[0] == "سوال درباره موجود بودن جنس" or previous_intent[0] == "سوال درباره قیمت جنس" or previous_intent[0]=="درخواست جنس") and previous_intent[1]:
                        product = previous_intent[1]
                        ShoppingList.objects.create(customer=customer_id, product=product, count=count)
                        return f"بفرمایید  اینم {count} تا {product.name} ", (None, None), False
                    msg_list = [" از چی {} تا بدم بهت ", " چه جنسی میخای {} تا بدم بهت  ", "چیو منظورته {} تا بدم بت؟", "چه چیزی رو میخای {} تا بدم بهت جناب؟"]
                    return choice(msg_list).format(count), ("گفتن تعداد جنس", count), False  ##
                                       
                if first_chat_obj.intent.title == "سوال درباره موجود بودن جنس":
                    if (previous_intent[0] == "سوال درباره قیمت جنس" or previous_intent[0] == "درخواست جنس") and previous_intent[1]:
                        product = previous_intent[1]
                        return f"بله هرچقدر بخایید {product.name} داریم", ("سوال درباره موجود بودن جنس", product), False
                    msg_list = ["چه جنسی رو میگی {} تا داریم یا نه؟", "چه جنسی منظورته {} تا داریم", "چه چیزی رو {} تا داریم ؟"]
                    return choice(msg_list).format(count), ("سوال درباره موجود بودن جنس", None), False
                    
                if first_chat_obj.intent.title == "سوال درباره قیمت جنس":
                    if (previous_intent[0] == "سوال درباره موجود بودن جنس" or previous_intent[0] == "درخواست جنس") and previous_intent[1]:
                        product = previous_intent[1]
                        return f"{product.name} {count} تاش میشه {product.price*count}", ("سوال درباره قیمت جنس", product), False
                    return f"چه چیزی {count} تاش چنده", ("سوال درباره قیمت جنس", count), False
                
          
        else:
            if product_qs.filter(exist=True):
                product = product_qs.filter(exist=True).first()
                
                if first_chat_obj.intent.title == "درخواست جنس":
                    if previous_intent[1] and isinstance(previous_intent[1], int):
                        count=previous_intent[1]
                        ShoppingList(customer=customer_id, product=product, count=count)
                        msg_list = ["بفرما قربان اینم {} تا {}", "بفرما اینم {} تا {} برای اعلی حضرت"]
                        return choice(msg_list).format(count, product.name), (None, None), False
                    msg_list = ["چند تا {} میخاید", "چند تا {} بدم بهت", "خب چند تا {}"]
                    return choice(msg_list).format(product.name), ("درخواست جنس", product), False
                
                if first_chat_obj.intent.title == "سوال درباره موجود بودن جنس":
                    msg_list = ["{} به تعداد بالا داریم" , "بله {} هم اینجا داریم هم انبار", "اره {} هم داریم"]
                    return choice(msg_list).format(product.name), ("سوال درباره موجود بودن جنس", product), False
                
                if first_chat_obj.intent.title == "سوال درباره قیمت جنس":
                    msg_list = ["{} دونه ای {} تومنه", "{} هر دونه {} تومان میباشد"]
                    return choice(msg_list).format(product.name, product.price), ("سوال درباره قیمت جنس", product), False
                 
            else:
                if first_chat_obj.intent.title == "سوال درباره موجود بودن جنس":
                    if (previous_intent[0] == "سوال درباره قیمت جنس" or previous_intent[0] == "درخواست جنس") and previous_intent[1]:
                        product = previous_intent[1]
                        return f"بله {product.name} داریم", ("سوال درباره موجود بودن جنس", product), False
                    msg_list = ["چه جنسی رو میگی", "چه جنسی منظورته منظورته؟", "چه چیزی ؟"]
                    return choice(msg_list), ("سوال درباره موجود بودن جنس", None), False
                
                if first_chat_obj.intent.title == "سوال درباره قیمت جنس":
                    if (previous_intent[0] == "سوال درباره موجود بودن جنس" or previous_intent[0] == "درخواست جنس") and previous_intent[1]:
                        product = previous_intent[1]
                        return f"{product.name} دونه ای {product.price} تومنه  قابل نداره", ("سوال درباره قیمت جنس", product), False
                    msg_list = ["چی چنده", "چه جنسی چنده ", "چیو منظورته چنده؟", "چه چیزی چنده؟"]
                    return choice(msg_list), ("سوال درباره قیمت جنس", None), False

                if first_chat_obj.intent.title == "درخواست جنس":
                    if (previous_intent[0] == "سوال درباره موجود بودن جنس" or previous_intent[0] == "سوال درباره قیمت جنس") and previous_intent[1]:
                        product = previous_intent[1]
                        return f"چند تا {product.name} میخای", ("درخواست جنس", product), False
                    msg_list = ["چی بدم بهت", "چه جنسی میخای بدم بهت ", "چیو منظورته میخای بدم بت؟", "چه چیزی رو میخای بدم بهت جناب؟"]
                    return choice(msg_list), ("درخواست جنس", None), False
                
    ############################################################        
    ############################################################       
    ############################################################
    ############################################################  
    ############################################################
    ############################################################     
    ############################################################  
             
    else:
        if lttrs_to_num_qs:
            if product_qs.filter(exist=True):
                count = lttrs_to_num_qs.first().number
                product = product_qs.filter(exist=True).first()
                
                if previous_intent[0] == "سوال درباره موجود بودن جنس":
                    resault = f"بله جناب هرچند تا بخای {product.name} داریم"
                    return resault, ("درخواست جنس", product), False
                
                if previous_intent[0] == "سوال درباره قیمت جنس":
                    return f"{count} تا از {product.name} میکنه به عبارتی {product.price*count} تومان", (None, None), False ##
      
                ShoppingList.objects.create(customer=customer_id, product=product, count=count)
                msg_list = [msg.response for msg in Chat.objects.filter(intent="درخواست جنس و گفتن تعداد جنس")]
                return choice(msg_list), (None, None), False
                      
            else:
                count = lttrs_to_num_qs.first().number
                if previous_intent[0] == "درخواست جنس":
                    product = previous_intent[1]
                    if not product:
                        return f"{count} تا چی؟", ("گفتن تعداد جنس", count), False
                    ShoppingList.objects.create(customer=customer_id, product=product, count=count)
                    msg_list = [msg.response for msg in Chat.objects.filter(intent="گفتن تعداد جنس", previous_intent="درخواست جنس")]
                    msg = choice(msg_list)
                    return f"{msg}, {product.name} رو به سبد خریدتون اضافه کردم", (None, None), False
                
                msg_list = [msg.response for msg in Chat.objects.filter(intent="گفتن تعداد جنس", previous_intent=None)]
                msg = choice(msg_list)
                return f"{count} تا از {msg}", ("گفتن تعداد جنس", count), False
            
                    
        else:
            if product_qs.filter(exist=True):
                product = product_qs.filter(exist=True).first()   
                    
                if previous_intent[0] == "سوال درباره قیمت جنس":
                    if previous_intent[1] and isinstance(previous_intent[1], int):
                        count = previous_intent[1]
                        return f"{product.name} {count} تاش میشه به عبارتی {product.price*count} فاکینگ تومن", ("سوال درباره قیمت جنس", product), False ## #درخاست جنس رد کرده بودم  
                    return f"{product.name} دونه ای {product.price} تومنه  قابل شمارم نداره", ("سوال درباره قیمت جنس", product), False   #درخاست جنس رد کرده بودم  
                
                if previous_intent[0] == "گفتن تعداد جنس":
                    count = previous_intent[1]
                    ShoppingList.objects.create(customer=customer_id, product=product, count=count)
                    return f"اینم {count} تا {product.name} دیگه چی بدم جناب؟", (None, None), False
                       
                if previous_intent[0] == "سوال درباره موجود بودن جنس":
                    msg_list = ['آره عزیزم {} داریم', 'بله جناب {} موجوده', 'یسسس {} هم داریم']
                    resault = choice(msg_list).format(product.name)
                    return resault, ("سوال درباره موجود بودن جنس", product), False #درخاست جنس رد کرده بودم    
                
                msg_list = ["چنتا {} میخای بیب؟", "چنتا {} بدم دستت بیبی؟", "چنتا {} بدم جناب؟"]
                resault = choice(msg_list).format(product.name)
                return resault, ("درخواست جنس", product), False
                                  
            else:
                
                if chat_qs_sentence:
                    first_chat_obj_sentence = chat_qs_sentence.first()

                    if first_chat_obj_sentence.intent.title == "سلام و احوال پرسی":
                        qs_len = chat_qs_sentence.count()
                        choice_weights = list()
                        while(qs_len>0):
                            choice_weights.append(qs_len*5)
                            qs_len -= 1
                        chat = choices(chat_qs_sentence, k=1, weights=choice_weights)[0]
                        return chat.response, (None, None), False
                    
                    if first_chat_obj_sentence.intent.title == "درخواست قیمت کل":
                        shopping_list = ShoppingList.objects.filter(customer=customer_id)
                        total_price = 0
                        msg = ""
                        for purchase in shopping_list:
                            price = purchase.price
                            msg += f"{purchase.product.name} - {purchase.count} تا : {price} تومان\n"
                            total_price += price
                        msg += f"قیمت کل: {total_price}"
                        return msg, (None, None), False
                    
                    if first_chat_obj_sentence.intent.title == "خداحافظی و حساب کتاب":
                        shopping_list = ShoppingList.objects.filter(customer=customer_id)
                        total_price = 0
                        msg = ""
                        for purchase in shopping_list:
                            price = purchase.price
                            msg += f"{purchase.product.name} - {purchase.count} تا : {price} تومان\n"
                            total_price += price
                        msg += f"قیمت کل: {total_price}\nخدا حافظ گل ناز"
                        shopping_list.delete()
                        return msg, (None, None), True      
                                
                msg_list = ['متوجه نشدم بهتر بگو', 'نمیفهمم چی میگی  درست بگو', 'میشه واضح تر بگی', 'درست بگو ببینم چی میگی']
                result = choice(msg_list)
                return result, (None, None), False
                
                    
    #end: True, False
    # current_intent --> (title of intent, product_obj or count(int))
    #return resault, current_intent ,end