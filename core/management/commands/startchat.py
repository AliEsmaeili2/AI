from django.core.management.base import BaseCommand
from core.chat_handler import introduction_text, guide_text, request_handler
from core.utils import customer_id_generator


class Command(BaseCommand):
    help = 'Make a conversation with bot'

    def handle(self, *args, **kwargs):
        customer_id = customer_id_generator()
        self.stdout.write(self.style.SUCCESS(introduction_text()))
        self.stdout.write(self.style.SUCCESS(guide_text()))
        self.stdout.write(self.style.WARNING(f"{'-'*40}\n{'-'*40}"))

        previous_intent = (None, None)
        
        while(True):
            user_request = input()    
            resault, previous_intent, end = request_handler(user_request, customer_id, previous_intent)
            self.stdout.write(self.style.SUCCESS(resault))
            if end:
                break