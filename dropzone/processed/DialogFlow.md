# DialogFlow

## 基本的概念

 ![](https://i.imgur.com/Q87X1tj.png)


- Google Home

  いわゆるスマートスピーカーで音声の入出力を取り扱う。OK Googleや ねぇGoogleでマイクをONにして、受け取った音声をGoogle Assistantに流す。

- Google Assistant

  受け取った音声を解析してニュースや音楽などを流す。また、場合によりActions on Googleのサービスを起動する。


- Actions on Google

  Google Assistantから呼び出せるサービスのこと。既存のアプリをActions on Googleに対応することでGoogle Assistantを経由して自社サービスやアプリなどを操作出来る様になる。

- Dialogflow

  言語解析エンジン
  音声入力で問題となりやすい自然言語の解析を簡単にやってくれる機能。


- Server

  Dialogflowから送られてきた解析済みのコマンドをServerで処理する。
  
  ここでよくFirebaseが紹介されるけれど、手っ取り早く無料でServerを立ち上げられるというだけの話で特にサーバーの縛りはなくて、Herokuでもいいし、実業務では多くの場合、既に稼働しているサーバーに接続する形になるはず。

  Dialogflowとの間はシンプルなJSONでのやり取りとなるため、既存サーバーと直接つなぐには既存サーバー側に対応したAPIを用意する必要がある。
  APIが用意されていないサービスと繋ぐために、スクレイピングや変換するサーバーを立てることもある。
  
  
- Intent

Android アプリ開発をしている人であれば、IntentというとActivityやServiceを起動する仕組みを思い浮かべるかもしれませんが、Dialogflowにおいては「ユーザーがやりたい事全体」を指すものになります。
Android開発者にとって紛らわしい名前がついているのはAlexa Skilの名称に合わせてきたのが理由かと思います。

- Entity

ユーザーから抽出したいキーワードがEntityです。
Entityには日付や住所と言った標準でDialogflowが抽出・解析できるSystem Entityに加えて、開発者が独自にDeveloper Entityを追加することもできます。

- FulfilIntent

解析した結果をサーバーに渡す処理がFulfilIntentです。サーバーとのやり取りはHTTPSが使用され内容はJSONのPUSHとレスポンスです。
FulfilIntentは必須ではなく、場合によってはDialogflow内に記載したIntentのResponseだけで完結することもあるかもしれませんが、基本的には、ユーザーのやりたい事（Intent)からキーワード（Entity）を抜き取ってサーバーに渡す（FulfilIntent）がDialogflowの流れとなります。


## DialogFlowとWebサイトの連携方法

Dialogflowで作成したチャットボットを実際に利用する方法をお伝えします。Dialogflowは大きく2つの利用方法があります。

- APIを使う

  APIを使いJSON形式でやりとりする方法です。Webサイト側で、ユーザーの文言入力を受け取る場所を用意し、そこから文言をDialogflowに送信、Dialogflowからの応答をサイトで受け取って、ユーザーに表示する、というページを用意します。

  文言のやりとりのみを行なうので、サイト上でのデザインやレイアウトなどは完全に自由。Node.js、PHP、Javaほか、様々な環境に向けたライブラリを、公式が配布してくれていますので、現行のサイトでも手軽に導入が可能です。

- Integrations（連携機能）を使う

  連携しているサービスの多さもDialogflowの魅力の一つです。LINE、Slack、Facebook Messengerをはじめ、様々なサービスでチャットボットを利用することができます。Webサイト用のチャットボットをそのままLINEでも活用することも可能です。

  さらに音声認識サービスとの連携も。特に、電話を用いた自動応答は注目です。作成したチャットボットで、そのままユーザーからの電話にも応答できます（2020年3月時点でベータ版）。




## DialogflowでAgentを作ってみる。

## Webhookを使う


## Dialogflow Messengerを使って、自分のサイトにAIチャットボットを設置する

* **Integrations**を開き、Dialogflow Messengerをクリックします。
* 埋め込み用のコードをコピーします

* 自分のサイトのbody閉じタグの直前あたりにコードを貼り付けます。



## 「Google Assistant」による多言語対応


これまでアシスタントアプリを開発する際は１つの言語に絞らなくてはいけませんでした。しかし、今回リリースされた機能を活用すれば英語にも日本語にも対応することが可能です。

現在14言語サポートしています。
※アシスタントのエミュレーターは現在９言語まで対応しています。


手順：
　
* 新規プロジェクト（アシスタントアプリ）の作成
* Intentの作成

* Google Assistantを試す

  * メニューからIntegrationsを選択
  * Google Assistantを選択
  * チェックボックスをONにする
  * Update Draftを押す
  * Closeで一回閉じる
  * 再びGoogle Assistantを選択する
  * TESTを押す
  * Test now active　View　を選択する
  * するとシュミレータが立ち上がるので「テスト用アプリにつないで」と話す
  * すると会話が始まるので「こんにちは」と話しかける
  * 先ほど設定した「こんにちは」が返ってくれば成功です


* 多言語対応する

   * さきほど同様IntegrationsからGoogle Assistantを選択する
   * 先ほど同様シュミレーターを立ち上げる
   * 言語をEnglish United Statusにする
   * 「Talk to my test app」と話しかける
   * 「Hello」と話し Hi! What can i help you?が返ってくれば成功！



## アーキテクチャ

Dialogflowを使ったチャットボットサービスのシステム構成例:




1. Dialogflowとインテグレーションしているサービスとつなぐ

![](https://i.imgur.com/BEV5eeU.png)

2. Dialogflowとインテグレーションしていない既成サービスとつなぐ
![](https://i.imgur.com/JcpA8Ga.png)

3. Dialogflowとインテグレーションしていない自作サービスとつなぐ

![](https://i.imgur.com/9SdN3mv.png)

※Dialogflowとインテグレーションしている：GoogleAssistantやSlackなどのサービスと連携して、サービス-Dialogflow間のリクエスト・レスポンスのやり取りが保障されている仕組み。サービスとDialogflowの設定だけでそれぞれをつなぐことができる。


4. 会議室予約例

![](https://i.imgur.com/5GxdQny.png)

① ユーザよりWebex Teams上のチャットで文字入力（例.明日予約）
② Webex Teamsへの入力内容がWebex BotによりDialogflowへ通知されます。
なお上記Webex TeamsへのIntegrations機能を利用するには、Webex Botのトークン情報をDialogflow上に登録しておく必要があります。
（参考：https://cloud.google.com/dialogflow/docs/integrations/spark）
③ Dialogflowで入力メッセージ内容を判別し、外部サービス連携機能（Fullfillment）を利用することでAmazon API Gatewayを通じ、AWS Lambda上にセットされた関数をコールします。
④ ③で呼び出された処理（会議室情報取得、予約）に応じたOutlook会議室情報を操作するためのOutlook APIをコールします。
⑤ 最後にWebex Botを通じWebex Teams上にOutlookでの操作結果を通知します。


## 料金

DialogFlowの料金

料金プランは個人・中小事業向け（Standard Edition）、大規模事業向け（Enterprise Edition）の2つに分けられます。 Standard Editionは基本的に無料です。Enterprise Editionは有料ですが、サポートの拡充や、リクエスト上限の引き上げが受けられます。




|  | Standard Edition | Enterprise Edition（Essentials） |
| -------- | -------- | -------- |
| テキスト認識     | •無料 •1分に180リクエストまで     | •$0.002/1リクエスト •1分に600リクエストまで     |
| 音声認識     | •無料 <br> •制限は音声認識と同じ     | •通常音声　$4/1,000文字 <br> •WaveNet音声 $16/1,000文字 <br> •制限は音声認識と同じ  |
| 音声出力     | •利用不可     | •〜1,000リクエストまで：1,000リクエストごとに$1.00 <br> •1,000〜5,000リクエストまで：1,000リクエストごとに$0.50  <br> •5,000〜20,000リクエストまで：1,000リクエストごとに$0.25     |
| 感情分析     | •利用不可     | •〜1,000リクエストまで：1,000リクエストごとに$1.00  <br>  •1,000〜5,000リクエストまで：1,000リクエストごとに$0.50  <br> •5,000〜20,000リクエストまで：1,000リクエストごとに$0.25     |
| 電話（ベータ版）<br> 音声認識・音声出力を含む     | •無料通話：無料 <br> •有料通話：利用不可  <br> •1分にのべ3分、<br>1日にのべ30分、1ヶ月にのべ500分まで    | •無料通話：$0.05/1分  <br> •有料通話：$0.06/1分  <br> •1分にのべ100分まで    |

※「有料通話」はユーザーが電話料金を払う番号での通話　


## サポート言語

Language table

Most Dialogflow ES features support all of these languages. As indicated by the table below, some features only support a subset of these languages. To filter the table, check your desired features. The filtered table only shows languages that support all selected features.

*  All
*  Text (text-only chat)
*  STT (speech-to-text, audio input, speech recognition)
*  TTS (text-to-speech, audio output, speech synthesis)
*  Phone (Dialogflow Phone Gateway with enhanced speech models disabled)
*  Knowledge (Knowledge Connectors)
*  Sentiment (Sentiment Analysis)
*  SmTalk (Built-in Small Talk)


| Name | Tag * | Text  |    STT  |    TTS  |    Phone  |    Knowledge  |    Sentiment  |    SmTalk |
| ----- | ----- | -----  |    -----  |    -----  |    -----  |    -----  |    -----  |    ----- |
| Bengali  |    bn  |    ✔  |      |      |      |      |      |      | 
| Bengali - Bangladesh  |    bn-BD  |    ✔  |      |      |      |      |      |      | 
| Bengali - India  |    bn-IN  |    ✔  |      |      |      |      |      |      | 
| Chinese - Cantonese  |    zh-HK  |    ✔  |    ✔  |    ✔  |      |      |      |      | 
| Chinese - Simplified  |    zh-CN  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
| Chinese - Traditional  |    zh-TW  |    ✔  |    ✔  |      |      |      |    ✔  |      | 
| Danish  |    da  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
| Dutch  |    nl  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
| English  |    en  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  | 
| English - Australia  |    en-AU  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |      |      | 
| English - Canada  |    en-CA  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |      |      | 
| English - Great Britain  |    en-GB  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |      |      | 
| English - India  |    en-IN  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |      |      | 
| English - US  |    en-US  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |      | 
| Filipino  |    fil  |    ✔  |      |      |      |      |      |      | 
| Filipino - The Philippines  |    fil-PH  |    ✔  |      |      |      |      |      |      | 
| Finnish  |    fi  |    ✔  |      |      |      |      |      |      | 
| French  |    fr  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |    ✔  | 
| French - Canada  |    fr-CA  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
| French - France  |    fr-FR  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
| German  |    de  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
| Hindi  |    hi  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
| Indonesian  |    id  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
| Italian  |    it  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |    ✔  | 
| Japanese  |    ja  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
| Korean  |    ko  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
| Malay  |    ms  |    ✔  |    ✔  |    ✔  |      |      |    ✔  |      | 
| Malay - Malaysia  |    ms-MY  |    ✔  |    ✔  |    ✔  |      |      |    ✔  |      | 
| Marathi  |    mr  |    ✔  |      |      |      |      |      |      | 
| Marathi - India  |    mr-IN  |    ✔  |      |      |      |      |      |      | 
| Norwegian  |    no  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
| Polish  |    pl  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
| Portuguese - Brazil  |    pt-BR  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
| Portuguese - Portugal  |    pt  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
| Romanian  |    ro  |    ✔  |      |      |      |      |      |      | 
| Romanian - Romania  |    ro-RO  |    ✔  |      |      |      |      |      |      | 
| Russian  |    ru  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |    ✔  | 
| Sinhala  |    si  |    ✔  |      |      |      |      |      |      | 
| Sinhala - Sri Lanka  |    si-LK  |    ✔  |      |      |      |      |      |      | 
| Spanish  |    es  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
| Spanish - Latin America  |    es-419  |    ✔  |    ✔  |      |      |      |    ✔  |      | 
| Spanish - Spain  |    es-ES  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
| Swedish  |    sv  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
| Tamil  |    ta  |    ✔  |      |      |      |      |      |      | 
| Tamil - India  |    ta-IN  |    ✔  |      |      |      |      |      |      | 
| Tamil - Sri Lanka  |    ta-LK  |    ✔  |      |      |      |      |      |      | 
| Tamil - Malaysia  |    ta-MY  |    ✔  |      |      |      |      |      |      | 
| Tamil - Singapore  |    ta-SG  |    ✔  |      |      |      |      |      |      | 
| Telugu  |    te  |    ✔  |      |      |      |      |      |      | 
| Telugu - India  |    te-IN  |    ✔  |      |      |      |      |      |      | 
| Thai  |    th  |    ✔  |    ✔  |      |      |      |    ✔  |      | 
| Turkish  |    tr  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
| Ukrainian  |    uk  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
| Vietnamese  |    vi  |    ✔  |      |      |      |      |    ✔  |      | 
| Vietnamese - Vietnam  |    vi-VN  |    ✔  |      |      |      |      |    ✔  |      | 

※ anguage tags follow the HTTP/1.1 specification, section 3.10.



## 参照

https://cloud.google.com/dialogflow




[Dialogflow入門](https://qiita.com/kenz_firespeed/items/0979ceb05e4e3299f313)


[チャットボットを自在に作成](https://wk-partners.co.jp/homepage/blog/webservices/dialogflow/)

[Dialogflow Language reference](https://cloud.google.com/dialogflow/es/docs/reference/language)


[【Dialogflow】ちょっと凝ったチャットボットを作りたい人が読むシステム構成の話](https://www.isoroot.jp/blog/1503/)



[Dialogflow(旧:API.AI) で多言語対応したGoogle Assistantアプリをサクッと作る #dialogflow](https://qiita.com/flatfisher/items/1de438d5213755a6bf27)


###### tags: `chatbot`