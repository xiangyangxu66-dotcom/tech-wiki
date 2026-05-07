# prototype

[toc]

## ドメインの設定

- domain.yml

```yaml=
version: "2.0"

intents:
  - greet
  - reserve

entities:
  - Time

slots:
  Time:
    type: text
    influence_conversation: false

responses:
  utter_greet:
    - text: "こんにちは！"
  utter_reserve:
    - text: "予約したい時間を入力してください。"
  utter_not_understand:
    - text: "すみません。よくわかりませんでした。"

forms:
  reservation_form:
    required_slots:
      Time:
        - type: from_entity
          entity: Time

actions:
  - action_reservation_time

session_config:
  session_expiration_time: 60
  carry_over_slots_to_new_session: true
```


### **intents**

intentsはボットを使用するユーザの入力の種類を記述します。 今回は予約チャットボットに対する挨拶であるgreetと、予約のトリガーとなるreserveの2つを使用することを宣言しています。 具体的にどのような言葉をどのintentとして定義するかはモデルの訓練時(後述)に決定されます。

### **entities**

entitiesには、ユーザの入力の中からボットが抽出したい固有表現を宣言します。 これらの表現はデータを用意して学習させることが可能なのですが、RasaではSpaCyの固有表現抽出機能をそのまま使用するためのパイプラインが整備されています(設定方法は後述)。 今回は入力された時間表現を抽出するために、GiNZAの固有表現名として定義されているTimeを使用します(GiNZAで抽出される固有表現はこちらを参照)。

### **slots**

slotsはボットが使用する変数を宣言します。 このslotの名前がentityと同じ名前である場合、entityが抽出された時に同名のslotに中身が自動的に挿入されます。 今回は、抽出されたentityであるTimeを保存するために用いる、テキストを値とするslotを作成しています。

### **responses**

responsesには、チャットボットがユーザへ返す内容を宣言します。 ボットへの挨拶の返答となるutter_greet、予約を促すutter_reserve、ユーザの入力が理解できなかった場合に返すutter_not_understandの3つを記述しています。



### **forms**

formsはユーザの入力から何かしらの情報を収集したい場合に使用します。 これらのformsは、required_slotsで指定されたslotsが全て埋まったかどうかを自動で判定します。 今回構築する予約チャットボットでは、予約時間Timeを保存するためのformを宣言しました。



### **actions**

Rasaではチャットボット自身のサーバとは別に、Action Serverと呼ばれるresponsesなどでは定義できないチャットボットの処理を定義したサーバと通信を行います。 このような処理はカスタムアクションと呼ばれ、このカスタムアクションの名前を宣言するのがactionsになります。 今回は予約の完了を通知するためのaction_reservation_timeというactionを用意しました。

カスタムアクションはactionディレクトリ以下の.pyファイルに定義されます。 今回は、プロジェクトに最初から用意されていたactions.pyを以下のように書き換えてカスタムアクションを定義しました。


```python=
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionReservationTime(Action):

    def name(self) -> Text:
        return "action_reservation_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        time = tracker.slots['Time']
        dispatcher.utter_message(text="{}に予約を完了しました！".format(time))

        return []
```

カスタムアクションはActionクラスを継承したクラスであり、最低でもname(self)とrun(self, dispatcher, tracker, domain)の2つのメソッドが定義されている必要があります(参考)。

Action.nameはカスタムアクションの名前を返すメソッドです。 これはdomain.ymlで宣言したアクション名からカスタムアクションを探すのに用いられるため、今回はaction_reservation_timeを返り値にしています。

Action.runにはカスタムアクションとして実際に実行される処理を書きます。
このメソッドの引数は以下の用途で使用されます。

* dispatcher: ユーザーにメッセージを返すために使用します。
* tracker: slotや過去のメッセージ等の状態を保持します。
* domain: domain.ymlに書かれたドメインの情報について保持しています。

ActionReserveTimeでは、trackerからslotであるTimeの中身を受け取って返信メッセージを作成しdispatcherに渡すことでボットへの返信を実現しています。 このように、ボットとの対話の状況に応じた複雑な処理を記述するためにカスタムアクションを使用することが可能です。

ちなみに、action_reservation_timeではslotの値に応じたメッセージを生成するためにカスタムアクションを使用しましたが、実際には同じ処理をresponseとして実現することが可能です。 今回はカスタムアクションの例を見せるためにカスタムアクションとして実装しました。
```

responses:
  utter_reservation_time:  # action_reservation_timeと同じ挙動
    - text: "{Time}に予約を完了しました！"
```
    
    


## モデルの設定


Rasaは自然言語理解(Natural Language Understanding, NLU)モデルを利用して、ユーザの入力したテキストからintentを予測したり、入力に対するactionの選択を行います。このモデルの設定はconfig.ymlというファイルに記載されます。

今回用いる設定は以下の通りです。この設定ファイルはlanguageとpipeline、policiesをキーに持つ連想配列となります。

```yaml=
language: ja

pipeline:
  - name: SpacyNLP
    model: 'ja_ginza'
  - name: SpacyTokenizer
  - name: SpacyFeaturizer
  - name: SpacyEntityExtractor
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: "char_wb"
    min_ngram: 1
    max_ngram: 4
  - name: DIETClassifier
    epochs: 100
  - name: EntitySynonymMapper
  - name: ResponseSelector
    epochs: 100

policies:
  - name: MemoizationPolicy
  - name: RulePolicy
  - name: TEDPolicy
    max_history: 5
    epochs: 100
```
    

### language

チャットボットで使用する言語を定義します。今回は日本語なのでjaを指定しています。

### pipeline

ユーザの入力テキストを処理するためのパイプラインを記述します。 前述の通りRasaはSpaCyとの強力な連携機能を有しており、SpaCyのトークナイズ機能・特徴量抽出機能・固有表現抽出機能を簡単に使うことが可能です。 例として、面倒な日本語でのトークナイズはパイプラインにname: SpacyTokenizerを追加するだけで解決してしまいます。

今回はRasaの公式がおすすめしている設定を元にSpacyNLPのmodelをGiNZAに変更、加えて固有表現抽出にGiNZAを用いるためのSpacyEntityExtractorを追加しました。

また、パイプラインの最後にFallbackClassifierを追加しています。 これを追加していると、ユーザの入力から予測できるintentの精度が閾値を下回る場合には、入力をnlu_fallbackというintentとみなすようになります。 予想外の入力がユーザからされた場合の対処を行うのに便利です。

その他のパイプラインの詳細については公式ページに詳しく記載されているため、そちらをご覧ください。

### policies

policiesはユーザの入力に対してボットがどのような対応をするかを決定するために使用されます。 今回の設定は推奨設定にRulePolicyを加えたものです。 RulePolicyを適用することで、モデル訓練のためのデータ(後述)にrulesを追加することが可能です。



## モデルの訓練データ

チャットボットのNLUモデルを訓練するためのデータはデフォルトではdataディレクトリ下に用意することになります。 決まったフォーマットに沿ったYAMLファイルであれば、ファイルをいくつに分けても問題はないようですが、今回は初期プロジェクトのファイル構成そのままに内容を変更しました。

### nlu

nluの値には、intentの例となる文を用意します。 今回のプロジェクトではdata/nlu.ymlとして保存しました。

ドメインで設定したように、ボットに対する挨拶となるgreetと予約をするためのトリガーであるreserveの2つのintentを宣言しているので、それらに対する入力の例を与えています。

```
version: "2.0"

nlu:

- intent: greet
  examples: |
    - こんにちは
    - おはようございます
    - こんばんは

- intent: reserve
  examples: |
    - 予約をする
    - 予約をお願いします
    - 予約をしたい
```

### rules

rulesは、あるintentや条件に対しての決まったアクションを提供します。 これはconfig.ymlにおいてRulePolicyを指定していない限り無効となります。

今回は、ユーザの入力がgreetとreserveのintentのどちらにも当てはまらない(Fallbackが発生する)場合にutter_not_understandレスポンスを返すように設定しています。
```

version: "2.0"

rules:

- rule: Fallback
  steps:
  - intent: nlu_fallback
  - action: utter_not_understand
```

### stories

storiesはユーザとボットの対話の例を示す訓練データです。 基本的にはユーザからのintentに対するボットの対応を記述していきます。

今回は、ユーザから挨拶をされた時に挨拶を返すgreetingと、予約をするためのreservationという2つのstoryを用意しています。

```
version: "2.0"

stories:

- story: greeting
  steps:
  - intent: greet
  - action: utter_greet
  - action: action_back


- story: reservation
  steps:
  - intent: reserve
  - action: utter_reserve
  - action: reservation_form
  - active_loop: reservation_form
  - active_loop: null
  - action: action_reservation_time
  - action: action_restart
```
以下に、それぞれのstoryがどのように進行するかを示します。

- greeting

  1. greetと予測されるintentが入力される
  1. utter_greetレスポンスを返す
  1. action_backアクションによりボットの状態を入力前に戻す

- reservation

  1. reserveと予測されるintentが入力される
  1. utter_reserveレスポンスを返す
  1. reservation_formをアクティブにする
  1. ユーザがTimeとなるentityを入力するまでループ
  1. Time entityが入力されたらaction_reservation_timeによるメッセージを表示
  1. action_restartアクションによりスロットを初期化する




## エンドポイント設定
モデルの設定やデータの準備は終わりましたが、最後にエンドポイントの設定をendpoints.ymlに書く必要があります。 今回はカスタムアクションを設定しているため、アクションサーバのエンドポイントを定義しておきます。

```
action_endpoint:
  url: "http://localhost:5055/webhook"
```

## モデル訓練
モデルの訓練は、プロジェクトのルートディレクトリで下記のコマンドを実行するだけです。 このコマンドはdomain.ymlやconfig.ymlの変更を気にしないため、もしこれらのファイルのみを変更して再学習を行いたい場合は、--forceをオプションを付ける必要があります。

`rasa train`
訓練されたモデルはmodelsディレクトリに置かれます。 何もオプションを指定していない場合はyyyymmdd-hhmmss.tar.gzという名前で保存されます。

## チャットボット実行

モデルを学習すると、実際にチャットボットを実行することが可能です。 ただし今回のようにカスタムアクションを定義している場合は、アクションサーバーを立てている必要があります。

`$ rasa run actions  &  # アクションサーバをバックグラウンドで実行`


CLIで対話的にチャットボットを実行するには、shellコマンドを使用します。


```

$ rasa shell

(省略)

Your input ->
実際に動いているかどうか確かめてみます。

Your input -> こんにちは
こんにちは！
Your input -> おはようございます
こんにちは！
Your input -> おはよう
こんにちは！  # data/nlu.ymlに定義されていない例でも正しく理解している
Your input -> あ
すみません。よくわかりませんでした。  # Fallbackの発生
Your input -> 予約したい
予約したい時間を入力してください。
Your input -> 15時
15時に予約を完了しました！
Your input -> 予約
予約したい時間を入力してください。  # data/nlu.ymlに定義されていない例でも正しく理解している
Your input -> 20:00にお願いします
20:00に予約を完了しました！  # 時間表現のみを正しく抽出している

```

###### tags: `chatbot`