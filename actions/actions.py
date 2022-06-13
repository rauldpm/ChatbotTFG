<<<<<<< HEAD
# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
=======
import pathlib
from typing import Text, List, Any, Dict, Optional

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

names = pathlib.Path("data/diccionarios/nombres.txt").read_text().split("\n")
malsonantes = pathlib.Path("data/diccionarios/malsonante.txt").read_text().split("\n")

class ValidateNameForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_name_form"

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        print("Required slots")

        first_name = tracker.slots.get("first_name")

        if first_name is not None:
            if first_name.lower() not in names:
                return ["name_spelled_correctly"] + slots_mapped_in_domain

        return slots_mapped_in_domain

    async def extract_name_spelled_correctly(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        print("extract_name_spelled_correctly")

        if len(tracker.slots.get("first_name")) <= 2:
            dispatcher.utter_message(text=f"Ese nombre es muy corto, dime otro mas largo (minimo 3 letras)")
            return {"first_name": None, "name_spelled_correctly": False, "first_name_save": None}

        return {"name_spelled_correctly": tracker.get_intent_of_latest_message() == "affirm"}

    def validate_name_spelled_correctly(
        self, slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""
        print("validate_name_spelled_correctly")

        intent = tracker.get_intent_of_latest_message()
        first_name = tracker.slots.get("first_name")
        first_name_save = tracker.slots.get("first_name_save")
        latest_message = tracker.latest_message['text']

        if first_name is not None:
            for string in malsonantes:
                if string in first_name:
                    dispatcher.utter_message("El nombre contiene una palabra no admitida: " + string + ". Por favor, utiliza otro nombre.")
                    return {"first_name": None, "name_spelled_correctly": None, "first_name_save": None}

        if (first_name_save is not None and intent == "affirm" and first_name_save != "/repetir_nombre"):
            names.append(first_name_save.lower())
            return {"first_name": first_name_save, "name_spelled_correctly": None, "first_name_save": None}

        elif (first_name_save is not None) and ((intent == "repetir_nombre") or (first_name == "/repetir_nombre")):
            if (first_name_save is not None and latest_message is not None and latest_message != first_name):
                return {"first_name": latest_message, "name_spelled_correctly": None, "first_name_save": None}
            if (first_name_save.lower() not in names and intent == "repetir_nombre" and first_name != "/repetir_nombre") or (intent == "deny"):
                buttons = [{'title': 'Yes', 'payload': '/affirm'}, {'title': 'No', 'payload': '/repetir_nombre'}]
                dispatcher.utter_message('Mmm esta bien escrito tu nombre? Si no, escribe tu nombre de nuevo', buttons=buttons)
                return {"first_name": None, "name_spelled_correctly": None, "first_name_save": latest_message}
            return {"first_name": None, "name_spelled_correctly": False, "first_name_save": latest_message}

        if tracker.get_intent_of_latest_message() != "repetir_nombre" or intent == "repetir_nombre":
            if latest_message is not None and latest_message != tracker.get_slot("first_name") and intent != "affirm":
                return {"first_name": latest_message, "name_spelled_correctly": None}
            buttons = [{'title': 'Yes', 'payload': '/affirm'}, {'title': 'No', 'payload': '/repetir_nombre'}]
            dispatcher.utter_message('Mmm esta bien escrito tu nombre? Si no, escribe tu nombre de nuevo', buttons=buttons)
            return {"first_name": None, "name_spelled_correctly": None, "first_name_save": tracker.get_slot("first_name")}

        return {"first_name": tracker.get_slot("first_name"), "name_spelled_correctly": None}

    def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""
        if slot_value is not None:
            print(f"First name given = {slot_value} length = {len(slot_value)}")
            if len(slot_value) <= 2:
                return {"first_name": None, "name_spelled_correctly": False }
            else:
                return {"first_name": slot_value}
        return {"first_name": None, "name_spelled_correctly": False }
>>>>>>> e7fd007 (Added unrecognized username loop, added more username recognition)
