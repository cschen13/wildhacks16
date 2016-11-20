from recognizer import Recognizer

r = Recognizer()
category = r.get_random_topic()
print "Category is {0}. Enter an image URL:".format(category)
url = raw_input()
print r.judge(category, url)