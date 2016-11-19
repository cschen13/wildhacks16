from clarifai.rest import ClarifaiApp
import json

app = ClarifaiApp()

model = app.models.get('general-v1.3')
url = 'https://www.extension.umd.edu/sites/default/files/resize/_images/programs/viticulture/table-grapes-74344_640-498x291.jpg'

# Hard-coded predictions
matches = {'banana', 'apple', 'orange'}
prediction = json.loads(json.dumps(model.predict_by_url(url)))

#print "STATUS CODE: {0}".format(prediction["status"]["code"])
found_match = False
for concept in prediction["outputs"][0]["data"]["concepts"]:
	if concept["name"] in matches and concept["value"] >= 0.85:
		print "IMAGE MATCH: {0}".format(concept["name"])
		found_match = True
		break;
if not found_match:
	print "NO MATCH FOUND"