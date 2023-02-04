import os
from airtable import Airtable
import os
from dotenv import load_dotenv
import openai
import json


### Constant
load_dotenv()
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
openai.api_key = os.environ.get('OPENAI_KEY')

### Airtable data information
BASE_ID = 'apph3SwLeTZGolkwK'
PROPERTY_TABLE_NAME = 'tblIGRh36Mdd63BCD'

## Initial prompt to set the scene
start_chat_log = '''You are a property manager (named Marvin) and a potential tenant reached out to you to get information about the available properties.
1. Provide all the information to potential tenants about the units available (if you do not know which unit he wants, generate questions to have the information)
2. Generate questions to retrieve all the information about the potential tenants by asking them questions
Providing answers to the tenant is top priority and should be done before generating questions to get to the profile. 

Your response must be in JSON format with the following field (only put the information if available, leave blank otherwise):
- "response": This is the response you are making to the potential tenant. It should include questions to know the tenant better in order to fill out all the info required
- "tenant_profile": Response in JSON formated to have all the required info about the tenant (first name, age, starting date desired, duration of lease desired, gender, occupation)
- "room_of_interest": JSON formatted response about the property of interest (city, address) and should be filled from the information from the tenant 

If asked about you (without mentions of units and we do not know which unit he wants, ask him), you can explain that you are the assistant of the owner and here to manage the properties.
'''

def ask(question, chat_log=None):
    prompt = f'{chat_log}Human: {question}\nAI:'
    response = openai.Completion.create(
        prompt=prompt, engine="text-davinci-003", stop=['\nHuman'], temperature=0.9,
        top_p=1, frequency_penalty=0.6, presence_penalty=0.6, best_of=1,
        max_tokens=500)

    print(response)
    tmp = json.loads(response.choices[0].text.strip())


    response = json.loads(response.choices[0].text.strip())

    answer = response['response']
    tenant_profile = response['tenant_profile']
    room_of_interest = response['room_of_interest']

    return answer, tenant_profile, room_of_interest

def append_interaction_to_chat_log(question, answer, chat_log=None):
    return f'{chat_log}Human: {question}\nAI: {answer}\n'

def get_all_property_info():
    at = Airtable(BASE_ID, api_key=AIRTABLE_API_KEY, table_name=PROPERTY_TABLE_NAME)
    records = at.get_all()
    return records

def get_all_property_available():
    all_prop = get_all_property_info()
    all_prop_avail = [prop['fields'] for prop in all_prop if prop['fields']['Status'] == 'Available']
    return all_prop_avail



## sandbox:

prop_available = get_all_property_available()
prop_available_dict = {}
for d in prop_available:
    prop_available_dict.update(d)

chat_log = start_chat_log + str(prop_available_dict)

question = 'Hello, I am interested in renting one of your room, can you give me more information. my name is charles, I am 18 and I am a data scientist here for an internship. I want a room in Annemasse '
answer, tenant_profile, room_of_interest = ask(question, chat_log)
chat_log = append_interaction_to_chat_log(question, answer, chat_log)

question = 'I want to rent for 1 year approximatively and I am looking for a place for me only. But do you have apartments or room for multiple persons'
answer, tenant_profile, room_of_interest = ask(question, chat_log)
chat_log = append_interaction_to_chat_log(question, answer, chat_log)

send_message(recipient_id, response_sent_text)