import json
import random
from clarifai.rest import ClarifaiApp

class Recognizer:
	def __init__(self, id=None, secret=None):
		self.app = ClarifaiApp(app_id=id, app_secret=secret)
		self.model = self.app.models.get('general-v1.3')
		self.categories = {
						   'fruit': ['fruit', 'apple', 'banana', 'orange', 'grapes', 'clementine', 'tangerine', 'grapefruit'],
						   'computer': ['computer', 'laptop'],
						   'selfie': ['portrait'],
						   'chair': ['chair', 'seat'],
						   'door': ['door', 'entrance'],
						   'backpack': ['backpack'],
						   'bottle': ['bottle'],
						   'drink': ['drink'],
						   'TV': ['television'],
						   'wood': ['wood', 'hardwood'],
						   'shoe': ['footwear', 'sneakers', 'shoe'],
						   'pair of jeans': ['denim'],
						   'phone': ['telephone'],
						   'glasses': ['eyewear', 'eyeglasses', 'sunglasses']
						  }
		self.threshold = 0.90

	def get_random_topic(self):
		print "Categories are: {0}".format(self.categories.keys())
		topic = random.choice(self.categories.keys())
		if topic == 'fruit' or topic == 'drink':
			self.model = self.app.models.get('food-items-v1.0')
		else:
			self.model = self.app.models.get('general-v1.3')
		return topic

	def judge(self, category=None, url=None):
		if url is None or category is None:
			return False
		prediction = json.loads(json.dumps(self.model.predict_by_url(url)))
		#print prediction

		#print "STATUS CODE: {0}".format(prediction["status"]["code"])
		for concept in prediction["outputs"][0]["data"]["concepts"]:
			if concept["name"] in self.categories[category] and concept["value"] >= self.threshold:
				print "IMAGE MATCH: {0}".format(concept["name"])
				return True
		print "NO MATCH"
		return False
