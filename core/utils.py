from time import time
from random import choices
from string import digits, ascii_letters


def customer_id_generator():  
    return "".join(choices(ascii_letters+digits, k=12)) + '-' + str(time())