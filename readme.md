# ComplaintBuddy - The Complaint Management Rasa Bot

### File Structure
```bash
├── actions
│   ├── actions.py
│   └── __init__.py
├── config.yml
├── credentials.yml
├── data
│   ├── nlu.yml
│   ├── rules.yml
│   ├── stories.yml
│   ├── testing_intents.yaml
│   └── training_intents.yaml
├── db_sqlite.py
├── document.odt
├── domain.yml
├── endpoints.yml
├── index.html
├── models
├── Rasa Core Visualisation.pdf
├── readme.md
├── requirements.txt
├── results
└── tests
```
### Customer Complaint Intents Handled by the NLU model
```
card_not_working
card_payment_not_recognised
card_swallowed
compromised_card
declined_transfer
unable_to_verify_identity
```

## Flow of the Rasa Chatbot

-The user initiates the Conversation with a greeting (example: ‘Hi’).  
-The chatbot initiates the ```Activalte User Info Form``` rule:  
  -The chatbot uses ```utter_greet``` response to greet the user  
  -The chatbot then activates the ```user_info_form``` form to collect the following information from the user  

```
account_no: text
first_name: text
last_name: text
email: text
phone_no: text
```

- The ```Submit User Info Form``` Rule is initiated to submit the information entered by the user.
- The chatbot uses the ```utter_submit``` response to respond to the user with a message(“Thank you for your response.”)
- The chatbot uses the ```utter_slots_values``` response to respond to the user with a message(“Hi, {name}, how can I help you today?”)
- The chatbot uses ```action_listen``` to get the response from the user
- The response of the user is classified with an intent, and based in the recognised intent, the corresponding rule gets triggered.

e.g.
```
- rule: Handle Card Not Working Complaints
  steps:
  - intent: card_not_working
  - action: action_record_text
  - action: utter_sorry_for_inconvenience
  - action: utter_card_not_working_faq
  - action: utter_has_your_problem_been_resolved
  - action: user_response_form
  - active_loop: user_response_form
```
This rule handles the responses for which the identified intent is ```card_not_working```. In this case, the chatbot calls the ```action_record_text``` custom action, which sets the slot – ```complaint```  with the complaint_text entered by the user. 
Next, the rule uses the ```utter_sorry_for_inconvenience``` and displays ```utter_card_not_working_faq``` and then asks the user for confirmation if the problem being faced by the user was resolved by the FAQs stated by the chatbot using ```utter_has_your_problem_been_resolved```.

The ```user_response_form``` is initiated to colllect the response from the user in either ‘yes’ or ‘no’. The response is validated using a ```validate_user_response_form``` custom action.

The ```action_respond_back``` custom action checks for the value of the response and if the response of the user was:
```
- ‘yes’
  - dispatch response ‘utter_submit_complaint’
	- dispatch response ‘utter_goodbye’
- ‘no’
	- insert the fields into a sqlite database:
		- account_no
		- first_name
		- last_name
		- phone_no
		- email
		- complaint
		- date
		- status
	- dispatch message: ‘utter_complaint_submission_status’
  - dispatch message: ‘utter_goodbye’  
  - use twilio client to send a message to the user indicating success in registering the complaint`
```

![image](https://user-images.githubusercontent.com/115154499/198951561-039d0a90-7464-4428-a2f7-b4471f9cf130.png)

## Running ComplaintBuddy
- ```cd complaint_buddy``` 
- Use ```rasa train``` to train a model based on intents and examples mentioned in the nlu.yml file
- Open a new terminal and start the actions server ```rasa run actions```
- Go to the  other terminal and execute ```rasa shell``` to start interacting with the bot in the terminal window.

## Starting a conversation with ComplaintBuddy
```
- Start a conversation by greeting the chatbot(e.g. ‘Hi’, ‘Hello’ etc.)
- Provide the data as requested by the bot
- account_no (regex: ‘[0-9]{9-18}’)
- first_name (should not be null)
- last_name (should not be null)
- email (regex: ‘^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$’)
- phone_no (regex: ‘^(\+91[\-\s]?)?[0]?(91)?[789]\d{9}$’)
```
