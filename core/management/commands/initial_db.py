from django.core.management.base import BaseCommand
from core.models import Chat, Product, Intent, LettersToNumber
import json

class Command(BaseCommand):
    help = 'Initial tables with json files'
    
    def initial_intent(self):
        with open('core/datasets/intents.json', 'r') as f:
            intents = json.load(f)   
        count = 0         
        for intent in intents:
            obj, created = Intent.objects.update_or_create(
                id = intent["id"],
                defaults={"title":intent['title']}
            )
            if created:
                count += 1
        return f'{count} Intent object created'
        
            
    def initial_chats(self):
        with open('core/datasets/chats.json', 'r') as f:
            chats = json.load(f) 
               
        count = 0
        for chat in chats:
            previous_intent = Intent.objects.filter(title=chat["previous_intent"]).first()
            intent = Intent.objects.filter(title=chat["intent"]).first()
            if intent:    
                obj, created = Chat.objects.update_or_create(
                    id = chat["id"],
                    defaults={
                        "previous_intent":previous_intent,
                        "intent":intent,
                        "request":chat['request'],
                        "response":chat['response']
                    }
                )
                if created:
                    count += 1
        return f'{count} Chat object created'
    
    
    def initial_products(self):
        with open('core/datasets/products.json', 'r') as f:
            products = json.load(f) 
        count = 0
        for product in products:
            obj, created = Product.objects.update_or_create(
                id=product["id"],
                defaults={
                    "name":product['name'],
                    "price":product['price'],
                    "exist":product["exist"],
                }
            )
            if created:
                count += 1
        return f'{count} Product object created'
    
    
    def initial_letters_to_number(self):
        with open('core/datasets/letters_to_number.json', 'r') as f:
            lttrs_to_nums = json.load(f) 
        count = 0
        for ltn in lttrs_to_nums:
            obj, created = LettersToNumber.objects.update_or_create(
                id = ltn["id"],
                defaults={
                   "letters":ltn['letters'],
                   "number":ltn['number']
                }
            ) 
            if created:
                count += 1
        return f'{count} LettersToNumber object created'    
            

    def handle(self, *args, **kwargs):
        # Intent objects must be create befor Chat objects
        info = self.initial_intent()
        self.stdout.write(self.style.SUCCESS(info))
        
        info = self.initial_chats()
        self.stdout.write(self.style.SUCCESS(info))
        
        info = self.initial_products()
        self.stdout.write(self.style.SUCCESS(info))
        
        info = self.initial_letters_to_number()
        self.stdout.write(self.style.SUCCESS(info))
        
