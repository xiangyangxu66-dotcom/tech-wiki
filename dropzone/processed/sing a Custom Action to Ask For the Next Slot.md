


# Using a Custom Action to Ask For the Next Slot

As soon as the form determines which slot has to be filled next by the user, it will execute the action utter_ask_<form_name>_<slot_name> or utter_ask_<slot_name> to ask the user to provide the necessary information. If a regular utterance is not enough, you can also use a custom action action_ask_<form_name>_<slot_name> or action_ask_<slot_name> to ask for the next slot.
```
from typing import Dict, Text, List

from rasa_sdk import Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action


class AskForSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_cuisine"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(text="What cuisine?")
        return []
```

###### tags: `chatbot` `rasa`