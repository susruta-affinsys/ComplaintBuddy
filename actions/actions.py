import re
import datetime as dt
from asyncore import dispatcher
from typing import Any, Text, Dict, List
from typing import Optional
import matplotlib
import rasa_sdk
import rasa_sdk.executor
from matplotlib.pyplot import text

from twilio.rest import Client

TWILIO_ACCOUNT_SID = "AC94bed60a5933ee415d23d1c0447e0999"
TWILIO_AUTH_TOKEN = "296ff7a069800caace089a5181d74f0c"
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

from rasa_sdk import Action, Tracker
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
from db_sqlite import insert_data


def clean_name(name):
    return "".join([c for c in name if c.isalpha()])


class ValidateUserInfoForm(FormValidationAction):
    def name(self) -> text:
        return "validate_user_info_form"

    def validate_account_no(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        account = slot_value
        pattern = re.compile("[0-9]{9,18}")
        if not pattern.match(account):
            dispatcher.utter_message(text="Please recheck your account number")
            return {"account_no": None}
        return {"account_no": account}

    def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        first_name = clean_name(slot_value)
        if len(first_name) == 0:
            dispatcher.utter_message(text="Please re-enter your first name")
            return {"first_name": None}
        return {"first_name": first_name}

    def validate_last_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        last_name = clean_name(slot_value)
        if len(last_name) == 0:
            dispatcher.utter_message(text="Please re-enter your last name")
            return {"last_name": None}
        return {"last_name": last_name}

    def validate_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        email = slot_value
        pattern = re.compile(
            "^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
        )
        if not pattern.match(email):
            dispatcher.utter_message(text="Please recheck your email-id")
            return {"email": None}
        return {"email": email}

    def validate_phone_no(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        phone_no = slot_value
        pattern = re.compile("^(\+91[\-\s]?)?[0]?(91)?[789]\d{9}$")
        if not pattern.match(phone_no):
            dispatcher.utter_message(text="Please re-enter your phone number")
            return {"phone_no": None}
        return {"phone_no": phone_no}


class ValidateUserResponseForm(FormValidationAction):
    def name(self) -> text:
        return "validate_user_response_form"

    def validate_response(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        resp = slot_value
        pattern = re.compile("^(?:yes|no)$")
        if not pattern.match(resp):
            dispatcher.utter_message(
                text="Sorry, I couldn't understand that. Please reply by typing 'yes' or 'no' only"
            )
            return {"response": None}
        return {"response": resp}


class ActionRecord(Action):
    def name(self):
        return "action_record_text"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        complaint_text = tracker.latest_message.get("text")
        return [SlotSet("complaint", complaint_text)]


class ActionReply(Action):
    def name(self):
        return "action_respond_back"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        slot_value = tracker.get_slot("response")
        if slot_value == "yes":
            dispatcher.utter_message(response="utter_submit_complaint")
            dispatcher.utter_message(response="utter_goodbye")
        elif slot_value == "no":
            date = dt.datetime.now()
            status = "In progress"
            insert_data(
                tracker.get_slot("account_no"),
                tracker.get_slot("first_name"),
                tracker.get_slot("last_name"),
                tracker.get_slot("phone_no"),
                tracker.get_slot("email"),
                tracker.get_slot("complaint"),
                date,
                status,
            )
            dispatcher.utter_message(response="utter_complaint_submission_status")
            dispatcher.utter_message(response="utter_goodbye")

            message = client.messages.create(
                to="whatsapp:+918420658782",
                from_="whatsapp:+14155238886",
                body="Your complaint has been registered and someone from the bank will contact you within 48 hours.",
            )
        return []
