# This file is used to verify your http server acts as expected
# Run it with `python3 test.py``
from datetime import datetime

import requests
from io import BytesIO
import base64
import banana_dev as banana

#Needs test.mp3 file in directory
with open(f'shorterTest.mp3','rb') as file:
    mp3bytes = BytesIO(file.read())
mp3 = base64.b64encode(mp3bytes.getvalue()).decode("ISO-8859-1")
model_payload = {"mp3BytesString":mp3, "useWordTranscription":True}

#res = requests.post("http://localhost:8000/",json=model_payload)
#print(res.text)


#use following to call deployed model on banana, model_payload is same as above
a_key = "c7637f21-d687-4c4b-8155-9efe679b2399"
m_key = "0b9c4bc7-41ba-4815-9613-1d2157f70c58"
startTime = datetime.now()
print ("Started Request",  str(startTime))
out = banana.run(a_key, m_key, model_payload)
totalTime = datetime.now() - startTime
print ("Finished Request in ", totalTime.seconds)
print (out)
