# Rasa UIの調査

[toc]

## Rasa Xの位置付け


- RasaXは、Rasaフレームワークを搭載したAIアシスタントの構築、改善、展開に役立つUIツールです。
- Rasaを単独で使用できます。RasaXオプション的なツールです。
- RasaXはオープンソースではなく、Community版が無料ですが、Enterprise版が有料です。


[rasa公式サイトにより](https://rasa.com/docs/rasa-x/0.21.5)
```
What Rasa X is:
Rasa X is a tool to learn from real conversations and improve your assistant.

Using it is totally optional. If you don’t want to, you can just use Rasa on its own.
What Rasa X is not:
It’s not a hosted service.

It’s not an all-in-one, point-and-click bot platform.
Rasa X is a tool that helps you build, improve, and deploy AI Assistants that are powered by the Rasa framework. Rasa X runs on your own computer and you can deploy it to your own server. None of your conversations or training data are ever sent anywhere.

We believe that great conversational AI is built by product teams. Some things, like inspecting and annotating conversations, are much easier with a UI. Rasa X focuses on those use cases and not on replacing things that are easier to do in code.

Rasa X comes in Community ($0) and Enterprise (paid) editions. The community edition is free but not open source, see the license and faq.
```



## Rasa UI Open Source Projects



当初、Rasaにはnluや対話管理などの対話用の主要なモジュールを提供されたが、使いやすいUI管理機能を持っていません。後に、NLU、DM、アクション、データ統計、およびユーザーコーパスの管理と注釈を統合するためツールRasaXをリリースしました。

RasaXがオープンソースではないため、本番レベルのアプリケーションが必要な場合は、対応するサービスパッケージを購入する必要があります。これに関連して、いくつかのオープンソースコミュニティはRasaX同等機能のツールを開発しました。中には有名なのは、次の通りです。


1. [botfront](https://botfront.io)
1. [articulate](https://github.com/samtecspg/articulate)
1. [RasaTalk](https://github.com/jackdh/RasaTalk)


その中で、1と3は基本的にRasaの元のnluとdmアーキテクチャを変更せず、Webインターフェイスを提供することにより、元の機能と上記のコーパス、モデル管理、データ統計などを改善します。
比較的には、Botfrontの方がは成熟しています。

また、上記のいずれものソースも、一年以上に更新されてない状態です。



### botfront

**Features**

* Build advanced multilingual conversational agents
* Write and train stories
* Create, train, and evaluate NLU models
* Create and edit your bot responses ‍
* Monitor conversations, review and annotate incoming NLU utterances


### Articulate

qiitaに纏まった文章です。全文を載せます。


Articulateは、自然言語理解エンジン Rasa NLU をベースにした「ビジネスチャットボットCMS」とでもいえるアプリケーションです。**Apacheライセンス**で、Smart Platform Groupが開発しています。


![](https://i.imgur.com/EVpK9PE.png)


Rasa NLUは、Rasa Technologiesが開発するオープンソースのNLUです。オープンソースのNLUではデファクトスタンダードのようなポジションで、Rasa NLUを使ったOSSが数多くあります。
ただし、Rasa NLUは残念ながら 日本語に未対応 です。（取り組んでみている人もいるようですが精度は不明）そのため、Articulateに日本語のトレーニングデータを登録しても、日本語を理解するボットを作ることは（現時点では）できません。


#### チャットボットを構成するためのCMS＆コンパネ

一般的に、チャットボットは様々なソフトウェアコンポーネントで構成されていますが、大きく分けて「表側」と「裏側」があります。

表側は、チャットユーザーに直接対応するアプリケーションです。質問や要求に答えたり、プロアクティブにメッセージを送ったりします。このとき「チャットユーザーの発言の意味」を理解するという過程でNLUを利用します。（NLUがチャットボットそのものであるかのように語られることもありますが、ソフトウェア全体としては部品の１つにすぎないのですよね）

裏側は、表側のアプリケーションのためのいわゆる「管理画面」です。チャットボットが回答に使用するコンテンツの登録、どのように回答するかのロジックやフローの登録、そしてNLUを訓練するためのトレーニングデータの登録などができます。

Articulateは、この「裏側」にフォーカスしたアプリケーションです。

オープンソースのチャットボットフレームワークやアプリケーションには、「表側」にフォーカスしたものが比較的多くあります。もちろん「裏側」が全くないチャットボットは成立しないので、いずれも多少なりとも機能をもってはいるのですが、裏側に「フォーカス」して作られているところが特徴的です。


#### エンタープライズで「運用される」ことが考えられた設計

Articulateは、エンタープライズでのチャットボット利用を意識して設計されているように見えます。設計者に知見があるのでしょう。

チャットボットは、実際に企業で利用すると「運用」が重要であることが分かります。構築段階から運用期間を通して、QA集め、コンテンツのチャット最適化、トレーニングデータ作成、チューニングなどの業務を繰り返し行うことになります。もちろん、自動化の余地は多いにあるものの、チャットボットの管理画面は半分「業務システム」みたいなところがあります。

オープンソースのプロダクトではこの「運用」というものが軽視されがちというか、エンジニアが作る前提であることが多いのですが、Articulateは、これをエンジニアでない人が継続的に行うために使うアプリケーションとして、概念や画面が整理されています。

**同じポジションのソフトウェアにRasa Core**がありますが、Rasa Coreよりも「ease of useを維持する方針」だそうです。


####  開発者向けアクションアイデア

エンジニアの方向けに、このOSSの活用アイデアや、コントリビュートしたいことについてのアイデアも残します。

- 日本語対応（表側）
  * 前述したように、Rasa NLU（およびDuckling）を前提としたソフトウェアなので、Rasa NLUで日本語を扱えるようにするようにしないと始まりません。
  * Articulateにおけるコンテンツやトレーニングデータで日本語テキストを扱うことは可能なので、Rasa NLUにコミットするか、あるいはオルタナティブを作るか。

- 日本語対応（裏側）
  * せっかく非エンジニア向けに設計された管理画面でも、日本人が運用できるようにするには、管理画面の文言も日本語にしないと厳しいですよね。
  * 管理画面の多国語化はサポートされていて、現時点で英語とスペイン語に対応しています。なので、日本語の言語リソースファイルさえあればできるのではと思います。（まず表側が対応しないと意味ないですが）


企業が開発しているということもありますが、質のよいOSSだと思うので、ぜひ試してみてください。UIはNode.jsで動くReactアプリケーションです。



## 開発業務でのWeb画面作成に参考になるサイト

### rasa-webchat(angular)

 (https://github.com/botfront/rasa-webchat)

**Features**

  - Text Messages
  - Quick Replies
  - Images
  - Carousels
  - Markdown support
  - Persistent sessions
  - Typing indications
  - Smart delay between messages
  - Easy to import in a script tag or as a React Compone


**スクリーンショット**

  ![](https://i.imgur.com/zKv8plH.png)

### vue-beautiful-chat(vue)
   
   (https://github.com/mattmezza/vue-beautiful-chat)

**Features**
   * Customizeable
   * Backend agnostic
   * Free

**スクリーンショット**


![](https://i.imgur.com/Tl3TfBG.png)



## 参考情報

https://www.opensourceagenda.com/tags/rasa-ui

https://botfront.io
https://github.com/botfront/rasa-webchat
https://medium.com/analytics-vidhya/create-a-simple-chatbot-with-rasa-x-and-integrate-with-web-6c8c9338ce3
https://forum.rasa.com/t/rasa-webchat-integration/19930
https://www.adoclib.com/blog/how-to-make-my-rasa-assistant-available-on-my-own-website.html
https://botfront.io/docs/rasa/getting-started/
https://www.youtube.com/watch?v=c1PlCE9eV5Q
https://zhuanlan.zhihu.com/p/78363022
https://zhuanlan.zhihu.com/p/78363022


https://qiita.com/nakmas/items/be611bdadabac0904e0c
https://www.youtube.com/watch?v=tXCYQ4BTjD0
https://www.datasciencecentral.com/articulate-open-source-platform-for-build-conversational/





###### tags: `chatbot`