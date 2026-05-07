     1|# Rasa UIの調査
     2|
     3|[toc]
     4|
     5|## Rasa Xの位置付け
     6|
     7|
     8|- RasaXは、Rasaフレームワークを搭載したAIアシスタントの構築、改善、展開に役立つUIツールです。
     9|- Rasaを単独で使用できます。RasaXオプション的なツールです。
    10|- RasaXはオープンソースではなく、Community版が無料ですが、Enterprise版が有料です。
    11|
    12|
    13|[rasa公式サイトにより](https://rasa.com/docs/rasa-x/0.21.5)
    14|```
    15|What Rasa X is:
    16|Rasa X is a tool to learn from real conversations and improve your assistant.
    17|
    18|Using it is totally optional. If you don’t want to, you can just use Rasa on its own.
    19|What Rasa X is not:
    20|It’s not a hosted service.
    21|
    22|It’s not an all-in-one, point-and-click bot platform.
    23|Rasa X is a tool that helps you build, improve, and deploy AI Assistants that are powered by the Rasa framework. Rasa X runs on your own computer and you can deploy it to your own server. None of your conversations or training data are ever sent anywhere.
    24|
    25|We believe that great conversational AI is built by product teams. Some things, like inspecting and annotating conversations, are much easier with a UI. Rasa X focuses on those use cases and not on replacing things that are easier to do in code.
    26|
    27|Rasa X comes in Community ($0) and Enterprise (paid) editions. The community edition is free but not open source, see the license and faq.
    28|```
    29|
    30|
    31|
    32|## Rasa UI Open Source Projects
    33|
    34|
    35|
    36|当初、Rasaにはnluや対話管理などの対話用の主要なモジュールを提供されたが、使いやすいUI管理機能を持っていません。後に、NLU、DM、アクション、データ統計、およびユーザーコーパスの管理と注釈を統合するためツールRasaXをリリースしました。
    37|
    38|RasaXがオープンソースではないため、本番レベルのアプリケーションが必要な場合は、対応するサービスパッケージを購入する必要があります。これに関連して、いくつかのオープンソースコミュニティはRasaX同等機能のツールを開発しました。中には有名なのは、次の通りです。
    39|
    40|
    41|1. [botfront](https://botfront.io)
    42|1. [articulate](https://github.com/samtecspg/articulate)
    43|1. [RasaTalk](https://github.com/jackdh/RasaTalk)
    44|
    45|
    46|その中で、1と3は基本的にRasaの元のnluとdmアーキテクチャを変更せず、Webインターフェイスを提供することにより、元の機能と上記のコーパス、モデル管理、データ統計などを改善します。
    47|比較的には、Botfrontの方がは成熟しています。
    48|
    49|また、上記のいずれものソースも、一年以上に更新されてない状態です。
    50|
    51|
    52|
    53|### botfront
    54|
    55|**Features**
    56|
    57|* Build advanced multilingual conversational agents
    58|* Write and train stories
    59|* Create, train, and evaluate NLU models
    60|* Create and edit your bot responses ‍
    61|* Monitor conversations, review and annotate incoming NLU utterances
    62|
    63|
    64|### Articulate
    65|
    66|qiitaに纏まった文章です。全文を載せます。
    67|
    68|
    69|Articulateは、自然言語理解エンジン Rasa NLU をベースにした「ビジネスチャットボットCMS」とでもいえるアプリケーションです。**Apacheライセンス**で、Smart Platform Groupが開発しています。
    70|
    71|
    72|![](https://i.imgur.com/EVpK9PE.png)
    73|
    74|
    75|Rasa NLUは、Rasa Technologiesが開発するオープンソースのNLUです。オープンソースのNLUではデファクトスタンダードのようなポジションで、Rasa NLUを使ったOSSが数多くあります。
    76|ただし、Rasa NLUは残念ながら 日本語に未対応 です。（取り組んでみている人もいるようですが精度は不明）そのため、Articulateに日本語のトレーニングデータを登録しても、日本語を理解するボットを作ることは（現時点では）できません。
    77|
    78|
    79|#### チャットボットを構成するためのCMS＆コンパネ
    80|
    81|一般的に、チャットボットは様々なソフトウェアコンポーネントで構成されていますが、大きく分けて「表側」と「裏側」があります。
    82|
    83|表側は、チャットユーザーに直接対応するアプリケーションです。質問や要求に答えたり、プロアクティブにメッセージを送ったりします。このとき「チャットユーザーの発言の意味」を理解するという過程でNLUを利用します。（NLUがチャットボットそのものであるかのように語られることもありますが、ソフトウェア全体としては部品の１つにすぎないのですよね）
    84|
    85|裏側は、表側のアプリケーションのためのいわゆる「管理画面」です。チャットボットが回答に使用するコンテンツの登録、どのように回答するかのロジックやフローの登録、そしてNLUを訓練するためのトレーニングデータの登録などができます。
    86|
    87|Articulateは、この「裏側」にフォーカスしたアプリケーションです。
    88|
    89|オープンソースのチャットボットフレームワークやアプリケーションには、「表側」にフォーカスしたものが比較的多くあります。もちろん「裏側」が全くないチャットボットは成立しないので、いずれも多少なりとも機能をもってはいるのですが、裏側に「フォーカス」して作られているところが特徴的です。
    90|
    91|
    92|#### エンタープライズで「運用される」ことが考えられた設計
    93|
    94|Articulateは、エンタープライズでのチャットボット利用を意識して設計されているように見えます。設計者に知見があるのでしょう。
    95|
    96|チャットボットは、実際に企業で利用すると「運用」が重要であることが分かります。構築段階から運用期間を通して、QA集め、コンテンツのチャット最適化、トレーニングデータ作成、チューニングなどの業務を繰り返し行うことになります。もちろん、自動化の余地は多いにあるものの、チャットボットの管理画面は半分「業務システム」みたいなところがあります。
    97|
    98|オープンソースのプロダクトではこの「運用」というものが軽視されがちというか、エンジニアが作る前提であることが多いのですが、Articulateは、これをエンジニアでない人が継続的に行うために使うアプリケーションとして、概念や画面が整理されています。
    99|
   100|**同じポジションのソフトウェアにRasa Core**がありますが、Rasa Coreよりも「ease of useを維持する方針」だそうです。
   101|
   102|
   103|####  開発者向けアクションアイデア
   104|
   105|エンジニアの方向けに、このOSSの活用アイデアや、コントリビュートしたいことについてのアイデアも残します。
   106|
   107|- 日本語対応（表側）
   108|  * 前述したように、Rasa NLU（およびDuckling）を前提としたソフトウェアなので、Rasa NLUで日本語を扱えるようにするようにしないと始まりません。
   109|  * Articulateにおけるコンテンツやトレーニングデータで日本語テキストを扱うことは可能なので、Rasa NLUにコミットするか、あるいはオルタナティブを作るか。
   110|
   111|- 日本語対応（裏側）
   112|  * せっかく非エンジニア向けに設計された管理画面でも、日本人が運用できるようにするには、管理画面の文言も日本語にしないと厳しいですよね。
   113|  * 管理画面の多国語化はサポートされていて、現時点で英語とスペイン語に対応しています。なので、日本語の言語リソースファイルさえあればできるのではと思います。（まず表側が対応しないと意味ないですが）
   114|
   115|
   116|企業が開発しているということもありますが、質のよいOSSだと思うので、ぜひ試してみてください。UIはNode.jsで動くReactアプリケーションです。
   117|
   118|
   119|
   120|## 開発業務でのWeb画面作成に参考になるサイト
   121|
   122|### rasa-webchat(angular)
   123|
   124| (https://github.com/botfront/rasa-webchat)
   125|
   126|**Features**
   127|
   128|  - Text Messages
   129|  - Quick Replies
   130|  - Images
   131|  - Carousels
   132|  - Markdown support
   133|  - Persistent sessions
   134|  - Typing indications
   135|  - Smart delay between messages
   136|  - Easy to import in a script tag or as a React Compone
   137|
   138|
   139|**スクリーンショット**
   140|
   141|  ![](https://i.imgur.com/zKv8plH.png)
   142|
   143|### vue-beautiful-chat(vue)
   144|   
   145|   (https://github.com/mattmezza/vue-beautiful-chat)
   146|
   147|**Features**
   148|   * Customizeable
   149|   * Backend agnostic
   150|   * Free
   151|
   152|**スクリーンショット**
   153|
   154|
   155|![](https://i.imgur.com/Tl3TfBG.png)
   156|
   157|
   158|
   159|## 参考情報
   160|
   161|https://www.opensourceagenda.com/tags/rasa-ui
   162|
   163|https://botfront.io
   164|https://github.com/botfront/rasa-webchat
   165|https://medium.com/analytics-vidhya/create-a-simple-chatbot-with-rasa-x-and-integrate-with-web-6c8c9338ce3
   166|https://forum.rasa.com/t/rasa-webchat-integration/19930
   167|https://www.adoclib.com/blog/how-to-make-my-rasa-assistant-available-on-my-own-website.html
   168|https://botfront.io/docs/rasa/getting-started/
   169|https://www.youtube.com/watch?v=c1PlCE9eV5Q
   170|https://zhuanlan.zhihu.com/p/78363022
   171|https://zhuanlan.zhihu.com/p/78363022
   172|
   173|
   174|https://qiita.com/nakmas/items/be611bdadabac0904e0c
   175|https://www.youtube.com/watch?v=tXCYQ4BTjD0
   176|https://www.datasciencecentral.com/articulate-open-source-platform-for-build-conversational/
   177|
   178|
   179|
   180|
   181|
   182|###### tags: `chatbot`