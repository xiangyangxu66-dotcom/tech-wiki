     1|# Dialogflow調査取りまとめ
     2|
     3|[TOC]
     4|
     5|
     6|Dialogflowは、Googleがサービス提供している無料から使えるチャットボットツールです。
     7|
     8|Webサイトにチャットボット設置でき、API連携で様々なWebツールとの連携も可能です。
     9|
    10| ![](https://i.imgur.com/Q87X1tj.png)
    11|
    12|
    13|## Dialogflowを使うチャットボットの作り方
    14|
    15|大まかな開発手順は以下となります。
    16|
    17|- Dialogflowでチャットボットを作る
    18|
    19|  - Googleアカウントでサインイン
    20|  - Dialogflowのアカウント作成
    21|  - 新規チャットボットの作成
    22|  - AIに言葉を登録する（Intentの作成）
    23|  - 応対する返答の設定（Responses）
    24|  - Entityの作成
    25|  - Intentsの設定
    26|  - 返答を作る（Responses）
    27|  - 様々な質問に応対するために複数の質問を登録
    28|
    29|- Dialogflowで作成したチャットボットをWebサイトに埋め込む
    30|
    31|   - 埋め込みコードの取得
    32|   - 取得したコードをWebページに貼付ける
    33|
    34|## コンセプト
    35|
    36|
    37|- Google Home
    38|
    39|  いわゆるスマートスピーカーで音声の入出力を取り扱う。OK Googleや ねぇGoogleでマイクをONにして、受け取った音声をGoogle Assistantに流す。
    40|
    41|- Google Assistant
    42|
    43|  受け取った音声を解析してニュースや音楽などを流す。また、場合によりActions on Googleのサービスを起動する。
    44|
    45|
    46|- Actions on Google
    47|
    48|  Google Assistantから呼び出せるサービスのこと。既存のアプリをActions on Googleに対応することでGoogle Assistantを経由して自社サービスやアプリなどを操作出来る様になる。
    49|
    50|- Dialogflow
    51|
    52|  言語解析エンジン
    53|  音声入力で問題となりやすい自然言語の解析を簡単にやってくれる機能。
    54|
    55|
    56|- Server
    57|
    58|  Dialogflowから送られてきた解析済みのコマンドをServerで処理する。
    59|  
    60|  ここでよくFirebaseが紹介されるけれど、手っ取り早く無料でServerを立ち上げられるというだけの話で特にサーバーの縛りはなくて、Herokuでもいいし、実業務では多くの場合、既に稼働しているサーバーに接続する形になるはず。
    61|
    62|  Dialogflowとの間はシンプルなJSONでのやり取りとなるため、既存サーバーと直接つなぐには既存サーバー側に対応したAPIを用意する必要がある。
    63|  APIが用意されていないサービスと繋ぐために、スクレイピングや変換するサーバーを立てることもある。
    64|
    65|
    66|## Dialogflowの基本
    67|
    68|- **エージェント(agent)**
    69|
    70|
    71|  Dialogflow エージェントは、エンドユーザーと会話を行う仮想エージェントであり、人間が使う言語のニュアンスを理解する自然言語理解モジュールです。Dialogflow はエンドユーザーの会話におけるテキストや音声を、アプリまたはサービスが理解できる構造化データに変換します。このラボでは、システムに求められている会話を処理するように Dialogflow エージェントを設計して作成します。
    72|
    73|  Dialogflow エージェントは、コールセンターの担当者と似ています。コールセンターの担当者の研修と同じように、予想される会話のシナリオに対処できるように Dialogflow エージェントのトレーニングを行いますが、完璧にやる必要はありません。
    74|
    75|
    76|- **インテント( Intent)**
    77|
    78|
    79|  インテントは、1 回の会話ターンにおけるエンドユーザーの意図を分類します。各エージェントで多数のインテントを定義し、複数のインテントを組み合わせて会話全体を処理します。エンドユーザーが書いたテキストや会話音声を「エンドユーザー表現」と呼び、Dialogflow はエンドユーザー表現をエージェント内の最適なインテントにマッチングさせます。インテントのマッチングは「インテント分類」とも呼ばれます。
    80|
    81|  たとえば、天気に関するエンドユーザーの質問を認識して回答する天気エージェントを作成するとします。この場合、天気予報の質問に対応するインテントを定義します。エンドユーザーが「今日の天気は？」と聞くと、Dialogflow はエンドユーザー表現を天気予報のインテントにマッチングさせます。また、インテントを定義してエンドユーザー表現から有用な情報（天気予報の時刻や場所など）を抽出することもできます。この抽出したデータは、エンドユーザーからの天気に関するクエリにシステムが回答するうえで重要です。
    82|
    83|
    84|![](https://i.imgur.com/vBMIA4B.png)
    85|
    86|基本的なインテントには次のものが含まれます。
    87|
    88|  - **トレーニング フレーズ**
    89|
    90|    エンドユーザーの会話に含まれる可能性があるフレーズのサンプルです。エンドユーザー表現がこれらのフレーズのいずれかと似ている場合、Dialogflow はインテントにマッチングします。Dialogflow に組み込まれている機械学習は他の類似のフレーズまで拡大して解釈するため、すべての例を定義する必要はありません。
    91|
    92|  - **アクション**
    93|    各インテントに対するアクションを定義します。インテントが一致すると、Dialogflow はシステムにアクションを提供します。ユーザーはそれを使用して、システムで定義済みの特定のアクションをトリガーできます。
    94|
    95|  - **パラメータ**
    96|    実行時にインテントが一致すると、Dialogflow はエンドユーザー表現から抽出した値をパラメータとして渡します。各パラメータには「エンティティ タイプ」というタイプがあります。エンティティ タイプは、抽出するデータの種類を定義するものです。未加工のエンドユーザー入力とは異なり、パラメータは構造化データです。ロジックを実行する際やレスポンスを生成する際に、パラメータを簡単に使用することができます。
    97|
    98|  - **レスポンス**
    99|    エンドユーザーに返すテキストまたは音声によるレスポンス、あるいは視覚的なレスポンスを定義します。エンドユーザーに回答したり、詳細を質問したり、会話を終了したりすることができます。
   100|  
   101|  
   102|次の図は、インテントのマッチングとエンドユーザーへのレスポンスの基本的なフローを示しています。
   103|
   104|![](https://i.imgur.com/V4fRqef.png)
   105|
   106|
   107|- **エンティティ**
   108|
   109|インテントの各パラメータには「エンティティ タイプ」と呼ばれるタイプがあります。エンティティ タイプは、エンドユーザーから抽出するデータの種類を定義するものです。
   110|
   111|Dialogflow には、多数の一般的なデータタイプに対応する事前に定義されたシステム エンティティが用意されています。たとえば、日付、時刻、色、メールアドレスなどをマッチングするためのシステム エンティティがあります。カスタムデータに対応する独自のカスタム エンティティを作成することもできます。
   112|
   113|- **コンテキスト**
   114|
   115|Dialogflow のコンテキストは、自然言語のコンテキストと似ています。たとえば、誰かが「それはオレンジです」と言った場合、「それ」が何を指しているのかを理解するためにコンテキストが必要になります。これと同じように、Dialogflow がそのようなエンドユーザー表現を適切なインテントにマッチングさせて処理するためには、コンテキストが必要になります。
   116|
   117|コンテキストを使用すると、会話のフローを制御できます。入力コンテキストと出力コンテキストを指定することで、インテントのコンテキストを設定できます（入力コンテキストと出力コンテキストは文字列形式の名前で指定します）。インテントが一致すると、そのインテント用に設定済みの出力コンテキストがアクティブになります。コンテキストが有効な場合、Dialogflow はその時点でアクティブなコンテキストに対応する入力コンテキストを使用して、構成済みのインテントに適切にマッチングできるようになります。
   118|
   119|- **フォローアップ インテント**
   120|
   121|フォローアップ インテントを使用すると、インテントのコンテキストのペアが自動的に設定されます。フォローアップ インテントは、関連する親インテントの子です。フォローアップ インテントを作成すると、出力コンテキストが自動的に親インテントに追加され、同じ名前の入力コンテキストがフォローアップ インテントに追加されます。前の会話ターンで親のインテントが一致した場合にのみフォローアップ インテントが一致します。複数階層のネスト構造でフォローアップ インテントを作成することもできます。
   122|
   123|Dialogflow には、「はい」、「いいえ」、「キャンセル」などの一般的なエンドユーザーの応答に対応する事前に定義されたフォローアップ インテントが数多くあります。カスタムの応答を処理する独自のフォローアップ インテントを作成することもできます。
   124|
   125|- **統合のためのフルフィルメント**
   126|
   127|デフォルトでは、エージェントは一致したインテントに静的レスポンスで応答します。いずれかの統合オプションを使用している場合は、フルフィルメントを使用して動的にレスポンスを返すことができます。インテントのフルフィルメントを有効にすると、Dialogflow は定義済みのサービスを呼び出してインテントに応答します。たとえば、エンドユーザーが金曜日にヘアカットの予定を入れる場合、サービスはデータベースをチェックし、金曜日の空き状況をエンドユーザーに返します。
   128|
   129|各インテントには、フルフィルメントを有効にするための設定があります。システムによるアクションや動的レスポンスを必要とするインテントの場合は、そのインテントでフルフィルメントを有効にします。フルフィルメントが有効になっていないインテントに一致した場合、Dialogflow はそのインテントで定義されている静的レスポンスを使用します。
   130|
   131|フルフィルメントが有効になっているインテントに一致した場合、Dialogflow はそのインテントに関する情報とともに Webhook サービスにリクエストを送信します。システムは必要なアクションを実行し、以降の処理方法に関する情報を Dialogflow に返します。次の図は、フルフィルメントの処理フローを示しています。
   132|
   133|### 処理フロー
   134|
   135|
   136|![](https://i.imgur.com/mNPAeDM.png)
   137|
   138|
   139|- Query	
   140|  自然言語の入力を受け取り、後段のIntentに合わせた構造化データ(JSON)に変換する
   141|
   142|- Intent
   143|  Queryで処理された構造化データを理解し、それに合わせた出力を返す
   144|
   145|- FulFillment
   146|  Intentでの処理を外部APIに移譲するための機構。webhookで構造化データを外部のエンドポイントにPOSTできる。複雑な処理や、既存システムにチャットボット機能を増設したい場合に活用する
   147|
   148|
   149|
   150|### DialogFlowとWebサイトの連携方法
   151|
   152|Dialogflowで作成したチャットボットを実際に利用する方法をお伝えします。Dialogflowは大きく2つの利用方法があります。
   153|
   154|- APIを使う
   155|
   156|  APIを使いJSON形式でやりとりする方法です。Webサイト側で、ユーザーの文言入力を受け取る場所を用意し、そこから文言をDialogflowに送信、Dialogflowからの応答をサイトで受け取って、ユーザーに表示する、というページを用意します。
   157|
   158|  文言のやりとりのみを行なうので、サイト上でのデザインやレイアウトなどは完全に自由。Node.js、PHP、Javaほか、様々な環境に向けたライブラリを、公式が配布してくれていますので、現行のサイトでも手軽に導入が可能です。
   159|
   160|- Integrations（連携機能）を使う
   161|
   162|  連携しているサービスの多さもDialogflowの魅力の一つです。LINE、Slack、Facebook Messengerをはじめ、様々なサービスでチャットボットを利用することができます。Webサイト用のチャットボットをそのままLINEでも活用することも可能です。
   163|
   164|  さらに音声認識サービスとの連携も。特に、電話を用いた自動応答は注目です。作成したチャットボットで、そのままユーザーからの電話にも応答できます（2020年3月時点でベータ版）。
   165|
   166|### Webhook
   167| 
   168| Webhooksはユーザー定義のHTTPコールバックである。通常、レポジトリにコードをプッシュしたり、ブログにコメントが投稿されたり等のイベントによりトリガーされる。
   169| 
   170| 一般的なAPIは利用者からAPIをコール（呼び出し）することで動作します。それに対してWebhookはあらかじめ設定したURLをサーバー側からコールすることができる仕組みです。Webコールバックとか、HTTPプッシュAPIと呼ばれることもあります。
   171|
   172|もっとざっくり言うと「アプリケーションAからアプリケーションBに対してリアルタイムな情報提供を実現するための仕組み」です。
   173|
   174|ここで、外部のWebサービスに対しPOSTリクエストを送信し、
   175|対話の内容をJSONで吐き出して他のWebサービスのAPIと連携してより詳細な情報を提供したり、情報等を外部のDBとのやりとりができるようになります。
   176|
   177|
   178|## アーキテクチャ例
   179|
   180|以下には、Dialogflowを使ったチャットボットサービスのシステム構成例です。
   181|
   182|
   183|1. Dialogflowとインテグレーションしているサービスとつなぐ
   184|
   185|![](https://i.imgur.com/BEV5eeU.png)
   186|
   187|2. Dialogflowとインテグレーションしていない既成サービスとつなぐ
   188|![](https://i.imgur.com/JcpA8Ga.png)
   189|
   190|3. Dialogflowとインテグレーションしていない自作サービスとつなぐ
   191|
   192|![](https://i.imgur.com/9SdN3mv.png)
   193|
   194|※Dialogflowとインテグレーションしている：GoogleAssistantやSlackなどのサービスと連携して、サービス-Dialogflow間のリクエスト・レスポンスのやり取りが保障されている仕組み。サービスとDialogflowの設定だけでそれぞれをつなぐことができる。
   195|
   196|
   197|4. 会議室予約例
   198|
   199|![](https://i.imgur.com/5GxdQny.png)
   200|
   201|① ユーザよりWebex Teams上のチャットで文字入力（例.明日予約）
   202|② Webex Teamsへの入力内容がWebex BotによりDialogflowへ通知されます。
   203|なお上記Webex TeamsへのIntegrations機能を利用するには、Webex Botのトークン情報をDialogflow上に登録しておく必要があります。
   204|（参考：https://cloud.google.com/dialogflow/docs/integrations/spark）
   205|③ Dialogflowで入力メッセージ内容を判別し、外部サービス連携機能（Fullfillment）を利用することでAmazon API Gatewayを通じ、AWS Lambda上にセットされた関数をコールします。
   206|④ ③で呼び出された処理（会議室情報取得、予約）に応じたOutlook会議室情報を操作するためのOutlook APIをコールします。
   207|⑤ 最後にWebex Botを通じWebex Teams上にOutlookでの操作結果を通知します。
   208|
   209|
   210|
   211|
   212|## 料金について
   213|
   214|DialogFlowの料金
   215|
   216|料金プランは個人・中小事業向け（Standard Edition）、大規模事業向け（Enterprise Edition）の2つに分けられます。 Standard Editionは基本的に無料です。Enterprise Editionは有料ですが、サポートの拡充や、リクエスト上限の引き上げが受けられます。
   217|
   218|
   219|
   220|
   221||  | Standard Edition | Enterprise Edition（Essentials） |
   222|| -------- | -------- | -------- |
   223|| テキスト認識     | •無料 •1分に180リクエストまで     | •$0.002/1リクエスト •1分に600リクエストまで     |
   224|| 音声認識     | •無料 <br> •制限は音声認識と同じ     | •通常音声　$4/1,000文字 <br> •WaveNet音声 $16/1,000文字 <br> •制限は音声認識と同じ  |
   225|| 音声出力     | •利用不可     | •〜1,000リクエストまで：1,000リクエストごとに$1.00 <br> •1,000〜5,000リクエストまで：1,000リクエストごとに$0.50  <br> •5,000〜20,000リクエストまで：1,000リクエストごとに$0.25     |
   226|| 感情分析     | •利用不可     | •〜1,000リクエストまで：1,000リクエストごとに$1.00  <br>  •1,000〜5,000リクエストまで：1,000リクエストごとに$0.50  <br> •5,000〜20,000リクエストまで：1,000リクエストごとに$0.25     |
   227|| 電話（ベータ版）<br> 音声認識・音声出力を含む     | •無料通話：無料 <br> •有料通話：利用不可  <br> •1分にのべ3分、<br>1日にのべ30分、1ヶ月にのべ500分まで    | •無料通話：$0.05/1分  <br> •有料通話：$0.06/1分  <br> •1分にのべ100分まで    |
   228|
   229|※「有料通話」はユーザーが電話料金を払う番号での通話　
   230|
   231|
   232|## サポート言語
   233|
   234|**サポート言語一覧**
   235|
   236|Most Dialogflow ES features support all of these languages. As indicated by the table below, some features only support a subset of these languages. To filter the table, check your desired features. The filtered table only shows languages that support all selected features.
   237|
   238|*  All
   239|*  Text (text-only chat)
   240|*  STT (speech-to-text, audio input, speech recognition)
   241|*  TTS (text-to-speech, audio output, speech synthesis)
   242|*  Phone (Dialogflow Phone Gateway with enhanced speech models disabled)
   243|*  Knowledge (Knowledge Connectors)
   244|*  Sentiment (Sentiment Analysis)
   245|*  SmTalk (Built-in Small Talk)
   246|
   247|
   248|| Name | Tag * | Text  |    STT  |    TTS  |    Phone  |    Knowledge  |    Sentiment  |    SmTalk |
   249|| ----- | ----- | -----  |    -----  |    -----  |    -----  |    -----  |    -----  |    ----- |
   250|| Bengali  |    bn  |    ✔  |      |      |      |      |      |      | 
   251|| Bengali - Bangladesh  |    bn-BD  |    ✔  |      |      |      |      |      |      | 
   252|| Bengali - India  |    bn-IN  |    ✔  |      |      |      |      |      |      | 
   253|| Chinese - Cantonese  |    zh-HK  |    ✔  |    ✔  |    ✔  |      |      |      |      | 
   254|| Chinese - Simplified  |    zh-CN  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
   255|| Chinese - Traditional  |    zh-TW  |    ✔  |    ✔  |      |      |      |    ✔  |      | 
   256|| Danish  |    da  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
   257|| Dutch  |    nl  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
   258|| English  |    en  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  | 
   259|| English - Australia  |    en-AU  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |      |      | 
   260|| English - Canada  |    en-CA  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |      |      | 
   261|| English - Great Britain  |    en-GB  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |      |      | 
   262|| English - India  |    en-IN  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |      |      | 
   263|| English - US  |    en-US  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |    ✔  |      | 
   264|| Filipino  |    fil  |    ✔  |      |      |      |      |      |      | 
   265|| Filipino - The Philippines  |    fil-PH  |    ✔  |      |      |      |      |      |      | 
   266|| Finnish  |    fi  |    ✔  |      |      |      |      |      |      | 
   267|| French  |    fr  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |    ✔  | 
   268|| French - Canada  |    fr-CA  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
   269|| French - France  |    fr-FR  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
   270|| German  |    de  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
   271|| Hindi  |    hi  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
   272|| Indonesian  |    id  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
   273|| Italian  |    it  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |    ✔  | 
   274|| Japanese  |    ja  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
   275|| Korean  |    ko  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
   276|| Malay  |    ms  |    ✔  |    ✔  |    ✔  |      |      |    ✔  |      | 
   277|| Malay - Malaysia  |    ms-MY  |    ✔  |    ✔  |    ✔  |      |      |    ✔  |      | 
   278|| Marathi  |    mr  |    ✔  |      |      |      |      |      |      | 
   279|| Marathi - India  |    mr-IN  |    ✔  |      |      |      |      |      |      | 
   280|| Norwegian  |    no  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
   281|| Polish  |    pl  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
   282|| Portuguese - Brazil  |    pt-BR  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
   283|| Portuguese - Portugal  |    pt  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
   284|| Romanian  |    ro  |    ✔  |      |      |      |      |      |      | 
   285|| Romanian - Romania  |    ro-RO  |    ✔  |      |      |      |      |      |      | 
   286|| Russian  |    ru  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |    ✔  | 
   287|| Sinhala  |    si  |    ✔  |      |      |      |      |      |      | 
   288|| Sinhala - Sri Lanka  |    si-LK  |    ✔  |      |      |      |      |      |      | 
   289|| Spanish  |    es  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
   290|| Spanish - Latin America  |    es-419  |    ✔  |    ✔  |      |      |      |    ✔  |      | 
   291|| Spanish - Spain  |    es-ES  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
   292|| Swedish  |    sv  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
   293|| Tamil  |    ta  |    ✔  |      |      |      |      |      |      | 
   294|| Tamil - India  |    ta-IN  |    ✔  |      |      |      |      |      |      | 
   295|| Tamil - Sri Lanka  |    ta-LK  |    ✔  |      |      |      |      |      |      | 
   296|| Tamil - Malaysia  |    ta-MY  |    ✔  |      |      |      |      |      |      | 
   297|| Tamil - Singapore  |    ta-SG  |    ✔  |      |      |      |      |      |      | 
   298|| Telugu  |    te  |    ✔  |      |      |      |      |      |      | 
   299|| Telugu - India  |    te-IN  |    ✔  |      |      |      |      |      |      | 
   300|| Thai  |    th  |    ✔  |    ✔  |      |      |      |    ✔  |      | 
   301|| Turkish  |    tr  |    ✔  |    ✔  |    ✔  |    ✔  |      |    ✔  |      | 
   302|| Ukrainian  |    uk  |    ✔  |    ✔  |    ✔  |    ✔  |      |      |      | 
   303|| Vietnamese  |    vi  |    ✔  |      |      |      |      |    ✔  |      | 
   304|| Vietnamese - Vietnam  |    vi-VN  |    ✔  |      |      |      |      |    ✔  |      | 
   305|
   306|※ anguage tags follow the HTTP/1.1 specification, section 3.10.
   307|
   308|
   309|
   310|## その他（メモ）
   311|
   312|
   313|### Dialogflow Messengerを使って、自分のサイトにAIチャットボットを設置する
   314|
   315|* **Integrations**を開き、Dialogflow Messengerをクリックします。
   316|* 埋め込み用のコードをコピーします
   317|
   318|* 自分のサイトのbody閉じタグの直前あたりにコードを貼り付けます。
   319|
   320|
   321|
   322|### 「Google Assistant」による多言語対応
   323|
   324|Dialogflowが30以上の言語と言語変種をサポートされます。
   325|
   326|
   327|作成手順：
   328|　
   329|* 新規プロジェクト（アシスタントアプリ）の作成
   330|* Intentの作成
   331|
   332|* Google Assistant
   333|
   334|  * メニューからIntegrationsを選択
   335|  * Google Assistantを選択
   336|  * チェックボックスをONにする
   337|  * Update Draftを押す
   338|  * Closeで一回閉じる
   339|  * 再びGoogle Assistantを選択する
   340|  * TESTを押す
   341|  * Test now active　View　を選択する
   342|  * するとシュミレータが立ち上がるので「テスト用アプリにつないで」と話す
   343|  * すると会話が始まるので「こんにちは」と話しかける
   344|  * 先ほど設定した「こんにちは」が返ってくれば成功です
   345|
   346|
   347|* 多言語対応する
   348|
   349|   * さきほど同様IntegrationsからGoogle Assistantを選択する
   350|   * 先ほど同様シュミレーターを立ち上げる
   351|   * 言語をEnglish United Statusにする
   352|   * 「Talk to my test app」と話しかける
   353|   * 「Hello」と話し Hi! What can i help you?が返ってくれば成功！
   354|
   355|### DialogflowのFulfillmentにAWS Lambdaを利用する
   356|  DialogflowのFulfillmentと、FulfillmentのWebhookをLambdaで実装する方法
   357|  
   358|  https://dev.classmethod.jp/articles/using_aws_lambda_for_fullfilment_of_dialogflow/#toc-5
   359|  
   360|
   361|## 参照
   362|
   363|https://cloud.google.com/dialogflow
   364|
   365|
   366|
   367|
   368|[Dialogflow入門](https://qiita.com/kenz_firespeed/items/0979ceb05e4e3299f313)
   369|
   370|
   371|[チャットボットを自在に作成](https://wk-partners.co.jp/homepage/blog/webservices/dialogflow/)
   372|
   373|[Dialogflow Language reference](https://cloud.google.com/dialogflow/es/docs/reference/language)
   374|
   375|
   376|[【Dialogflow】ちょっと凝ったチャットボットを作りたい人が読むシステム構成の話](https://www.isoroot.jp/blog/1503/)
   377|
   378|
   379|
   380|[Dialogflow(旧:API.AI) で多言語対応したGoogle Assistantアプリをサクッと作る #dialogflow](https://qiita.com/flatfisher/items/1de438d5213755a6bf27)
   381|
   382|
   383|[チャットボットの作り方](https://takapon.net/chatbot-dialogflow/#DialogflowWeb)
   384|
   385|
   386|[エージェント向けの会話フローの設計](https://www.cloudskillsboost.google/focuses/12347?locale=ja&parent=catalog&qlcampaign=1m-freelabs-277)
   387|
   388|
   389|[DialogflowのFulfillmentにAWS Lambdaを利用する](https://dev.classmethod.jp/articles/using_aws_lambda_for_fullfilment_of_dialogflow/)
   390|
   391|
   392|[Googleアシスタント と Vue.js を使ってスマートディスプレイアプリ](https://qiita.com/Ichiaki/items/5b28d243b49fa1e0af2d)
   393|
   394|
   395|
   396|[JavaアプリケーションにDialogflowを組み込む話](https://qiita.com/penguin_syan/items/ef4b451f14923aa17fc5)
   397|
   398|
   399|###### tags: `chatbot`