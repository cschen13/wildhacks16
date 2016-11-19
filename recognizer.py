from clarifai.rest import ClarifaiApp
import json

class Recognizer:
	def __init__(self):
		self.app = ClarifaiApp()
		self.model = self.app.models.get('general-v1.3')
		self.categories = {'fruit': ['fruit', 'apple', 'banana', 'orange', 'grapes'],
						   'computer': ['computer', 'laptop'],
						   'selfie': ['portrait']}
		self.threshold = 0.90

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