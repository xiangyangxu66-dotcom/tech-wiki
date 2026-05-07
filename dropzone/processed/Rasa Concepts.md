# Rasa Concepts

[toc]

## Domain

The domain defines the universe in which your assistant operates. It specifies the intents, entities, slots, responses, forms, and actions your bot should know about. It also defines a configuration for conversation sessions.


Here is a full example of a domain, taken from the concertbot example:

```
version: "3.0"

intents:
  - affirm
  - deny
  - greet
  - thankyou
  - goodbye
  - search_concerts
  - search_venues
  - compare_reviews
  - bot_challenge
  - nlu_fallback
  - how_to_get_started

entities:
  - name

slots:
  concerts:
    type: list
    influence_conversation: false
    mappings:
    - type: custom
  venues:
    type: list
    influence_conversation: false
    mappings:
    - type: custom
  likes_music:
    type: bool
    influence_conversation: true
    mappings:
    - type: custom

responses:
  utter_greet:
    - text: "Hey there!"
  utter_goodbye:
    - text: "Goodbye :("
  utter_default:
    - text: "Sorry, I didn't get that, can you rephrase?"
  utter_youarewelcome:
    - text: "You're very welcome."
  utter_iamabot:
    - text: "I am a bot, powered by Rasa."
  utter_get_started:
    - text: "I can help you find concerts and venues. Do you like music?"
  utter_awesome:
    - text: "Awesome! You can ask me things like \"Find me some concerts\" or \"What's a good venue\""

actions:
  - action_search_concerts
  - action_search_venues
  - action_show_concert_reviews
  - action_show_venue_reviews
  - action_set_music_preference

session_config:
  session_expiration_time: 60  # value in minutes
  carry_over_slots_to_new_session: true
```


### Intents
The intents key in your domain file lists all intents used in your NLU data and conversation training data.

intentsはボットを使用するユーザの入力の種類を記述します。 今回は予約チャットボットに対する挨拶であるgreetと、予約のトリガーとなるreserveの2つを使用することを宣言しています。 具体的にどのような言葉をどのintentとして定義するかはモデルの訓練時(後述)に決定されます。


### Entities



### Slots


### Responses

Responses are actions that send a message to a user without running any custom code or returning events. These responses can be defined directly in the domain file under the responses key and can include rich content such as buttons and attachments. For more information on responses and how to define them, see Responses.

### Forms
Forms are a special type of action meant to help your assistant collect information from a user. Define forms under the forms key in your domain file. For more information on form and how to define them, see Forms.


### Actions


## Training Data

### Data Format

Rasa Open Source uses YAML as a unified and extendable way to manage all training data, including NLU data, stories and rules.

- keys
  - version
  - nlu
  - stories
  - rules


- Example
Here's a short example which keeps all training data in a single file:
```
version: "3.0"

nlu:
- intent: greet
  examples: |
    - Hey
    - Hi
    - hey there [Sara](name)

- intent: faq/language
  examples: |
    - What language do you speak?
    - Do you only handle english?

stories:
- story: greet and faq
  steps:
  - intent: greet
  - action: utter_greet
  - intent: faq
  - action: utter_faq

rules:
- rule: Greet user
  steps:
  - intent: greet
  - action: utter_greet
```


### NLU Training Data

### Stories

### Rules



## Config

### pipeline

### Policies

### Language Support


###### tags: `chatbot`