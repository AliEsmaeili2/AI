from django.db import models

class Similarity(models.Func):
    function = "similarity"

class WordSimilarity(models.Func):
    function = "word_similarity"


""" 
    LettersToNumber.objects.annotate(
        match=Similarity("letters", models.Value("سه تا روغن بدید لطفا"))
    ).filter(match__gt=0.3).order_by("-match")

"""


class Chat(models.Model):
    #intent is mondatory
    #previous_intent is not mondatory
    
    previous_intent = models.ForeignKey(
        to='Intent', to_field='title',
        related_name='previous_chats', on_delete=models.CASCADE,
        blank=True, null=True
    )
    intent = models.ForeignKey(
        to='Intent', to_field='title',
        related_name='chats', on_delete=models.CASCADE
    )
    request = models.CharField(blank=True, max_length=50000)
    response = models.CharField(blank=True, max_length=50000)
    
    
class Intent(models.Model):
    title = models.CharField(unique=True, max_length=50000)
    

class Product(models.Model):
    name = models.CharField(unique=True, max_length=50000)
    price = models.BigIntegerField()
    exist = models.BooleanField()
    

class LettersToNumber(models.Model):
    letters = models.CharField(max_length=50000)
    number = models.BigIntegerField()


class ShoppingList(models.Model): 
    #customer id, generate random.
    customer = models.CharField(max_length=50)
    
    product = models.ForeignKey(
        to='Product', to_field='name', on_delete=models.CASCADE
    )
    count = models.IntegerField()
    
    @property
    def price(self):
        return self.product.price * self.count
    
    
