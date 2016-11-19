from recognizer import Recognizer
import random

r = Recognizer()
category = random.choice(r.categories.keys())
print "Category is {0}. Enter an image URL:".format(category)
url = raw_input()
print r.judge(category, url)