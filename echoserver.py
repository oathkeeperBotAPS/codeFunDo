import sys
from flask import request, Flask
import requests
import jsonData




app = Flask(__name__)

TOKEN = 'EAAG938KqkPoBAPHnGjuv3bQhgdAbALWfDAPHy1h8kX1sgdNPYjtzS4SAUOpZASXfDMRCS3ycdFzEMuIPLWtdy6NBFDrHKOrjEp40Dsa7gbhu80g4SANhOHBNDEVSsOZBL4WQSAbLqVboZAlBykv25671Yo1WacJG3U0UHh6FQZDZD'
baseUrl = 'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/'
sendUrl = 'https://graph.facebook.com/v2.6/me/messages'
app_id = '94d57e7b-86f8-44d3-9b63-9f6f8a0610b3'
subscription_key = '3fc2ab51520e473f8842f288fe2ec87a'






def NoneIntent(entities):
	rep = "Hi, I am Creo"
	return rep





def convoIntent(entities):
	for entity in entities:
		if entity['type'] == 'hayhello':
			try:
				rep = convoRep[entity['entity']]
			except:
				rep = "Hi, I am Creo"

	return rep



def getReply(jsonData):
	query = jsonData['query']
	topScoringIntent = jsonData['topScoringIntent']['intent']
	entities = jsonData['entities']

	return processIntent[topScoringIntent](entities)





def getResponse(query):
	headers = {
 	   'Ocp-Apim-Subscription-Key': subscription_key,
	}

	params ={
	    'q': query,
	    'timezoneOffset': '0',
	    'verbose': 'false',
	    'spellCheck': 'false',
	    'staging': 'false',
	}

	try:
	    r = requests.get(baseUrl + app_id,headers=headers, params=params)
	    try:
	    	json_data = r.json()
	    	res = getReply(json_data)
	    	return res
	    except Exception as e:
	    	return "Error in luis data"

	except Exception as e:
	    return "Error in request"




def analyseMsg(msg):
	msgId = msg['mid']
	try:
		query = msg['text']
		return getResponse(query)
	except:
		return "Hey, I am Creo"




def analyseData(entries):
	for entry in entries:
		pageId = entry['id']
		for msg in entry['messaging']:
			sender = msg['sender']['id']
			reply = analyseMsg(msg['message'])
			reply = reply.encode('unicode_escape')
			yield sender, reply






def sendReply(sender, reply):
	headers = {
		'Content-type' : 'application/json'
	}

	params = {
		'access_token' : TOKEN
	}

	data = json.dumps({
		'recipient' : {
			'id' : sender
		},

		'message' : {
			'text' : reply.decode('unicode_escape')
		}
	})

	r = requests.post(sendUrl, headers= headers, data=data, params=params)
	if r.status_code != requests.codes.ok:
		print("eroor")
		#with open('errorLog.txt') as errorLog:
			#errorLog.write(r.text)



processIntent = {
	'convo' : convoIntent,
	'None' : NoneIntent,
}


convoRep = {
	'hey' : "Hey, How's your day?",
	'hello' : "Hello, there. How was your day?",
	'hi' : "Hii, How did your day go?",
	'whatsup' : "All Good, How you doing?",
}




@app.route('/', methods=['GET'])
def verifyToken():
	token = request.args.get('hub.verify_token')
	if token == TOKEN:
		print("Verification Successful.")
		return request.args.get('hub.challenge')
	else:
		print('Verification Failed')
		return "Verification Failed."


@app.route('/', methods=['POST'])
def messageRecieved():
	payload = request.get_data()
	payload = json.loads(payload)
	#with open('messageLog.txt', 'a') as log:
		#log.write(payload['entry'])
		#log.write('------------------------------------------------')
	for sender, reply in analyseData(payload['entry']):
		sendReply(sender, reply)
	return 'ok'



if __name__=='__main__':
	app.run()
