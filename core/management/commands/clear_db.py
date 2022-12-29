from django.core.management.base import BaseCommand
from core.models import Chat, Product, Intent, LettersToNumber, ShoppingList


class Command(BaseCommand):
    help = 'Clear tables all'

    def handle(self, *args, **kwargs):
        deleted = Chat.objects.all().delete()
        self.stdout.write(self.style.WARNING(deleted))
        
        deleted = Product.objects.all().delete()
        self.stdout.write(self.style.WARNING(deleted))
        
        deleted = Intent.objects.all().delete()
        self.stdout.write(self.style.WARNING(deleted))
        
        deleted = LettersToNumber.objects.all().delete()
        self.stdout.write(self.style.WARNING(deleted))
        
        deleted = ShoppingList.objects.all().delete()
        self.stdout.write(self.style.WARNING(deleted))
        
        self.stdout.write(self.style.SUCCESS('Cleared!'))

