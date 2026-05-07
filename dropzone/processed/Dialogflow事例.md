
# Dialogflow事例

## 三菱UFJ銀行

三菱UFJ銀行では #GoogleCloud をコールセンター業務のチャットボット導入に利用。Dialogflow で開発したチャットボットによって、利用数、解決率ともに想定を大きく上回る成果を実現しています。




 2019 年 2 月、予定通りチャットボットを運用開始。三菱UFJ銀行公式 Web サイトに、個人向けインターネット バンキング（三菱UFJダイレクト）限定で「チャットで問い合わせる
 
 「チャットボットをインターネット バンキングという領域でリリースするのが初めてだったこともあり、当初はどういう問い合わせがあるのかも分かりませんでした。そこで、まずはコールセンターにいただくお問い合わせの中から、とりわけ件数の多いものにだけ対応する、スモール スタートという形で始めています。その後は、実際のお問い合わせ内容を分析して、新しいシナリオをリリースしたり、上手く機能しなかったシナリオについてはチューニングをかけていくということを毎週のようにやっていきました。」（多川さん）
 
 
 
リリース当初は約 30 件だったシナリオ数が、2019 年末の時点で約 150 件にまで増強。問い合わせの約 50 ～ 60％ に回答できるようになっていると言います。

「中でも断トツで多いのはログインができない、（複数存在する）パスワードのどれを使えばいいのか分からないといった質問ですね。また、これはリリースした後に分かったのですが、海外にお住まいのお客さまのチャット利用率が想像以上に多かったんです。チャットには電話代や時差の問題がありませんから。また、金融業界ならではの、季節性・突発性のある問い合わせにチャットボットで対応できる点も評価しています。例えば年末年始の休業日にいただいたたくさんのお問い合わせに対し、チャットボットでの解決率は 9 割越えを達成しています。近年、社会問題となっている詐欺メールに関する照会やキャンペーンへのお問い合わせ対応などにも活躍しているんですよ。」（多川さん）

![](https://i.imgur.com/bJAV447.png)



「とは言え AI のシナリオを増やしてチューニングしていくためには有識者の参加が不可欠ですし、質問内容や正解率のモニタリング体制もしっかり作り込んでいかねばなりません。このプロジェクトの目的はコストの削減ですから、月に 10 件あるかないかという照会原因に対して AI のシナリオ を作り込んでいくのは明らかに効果的ではありません。作るべきシナリオと、オペレーターに任せるシナリオの見極めをしていく必要があります。」（島野さん）



また、本来の目的であるコスト削減についても、効果の見極めが難しいことも悩みどころだと言います。

「当初から分かっていたことではあるのですが、お問い合わせの電話件数はその時々の社会情勢にも大きく左右されるため、1 年前の件数と今の件数を比較しても、それがチャットボットの成果なのかが分かりにくいんです。そこで現在はそれとは別の KPI、具体的にはチャットの利用件数、チャットボットの解決率、そしてチャットボットで解決できない質問を担当するオペレーターの対応単価の 3 つで効果を測定するということを始めています。結果、利用件数と解決率についてはそれぞれ当初の目標値を大きくクリアし、想定以上の効果が出ていることがわかりました。残念ながらオペレーターの対応単価については目標を達成できていないのですが、これはチャットボットの解決率が想定よりも高かったことで、予想よりもオペレーターに繋ぐ人が少なかったためだと考えています。オペレーターの配置人数については、今後は適正化されていくでしょう。」



「Dialogflow って、大げさに言うとログインするたびに新しい機能が追加されていくんですよ。せっかくなのでそうした機能は β 版であっても積極的に触っていくようにしています。たとえば最近だとエージェントの学習内容を検証するバリデーション機能を実際の運用で使い始めました。良くない言い回しや類義語をサジェストしてくれるので精度向上にとても役立っています。今後はこうした機能も駆使して、より効率的にチューニングを施していきたいですね。」（多川さん）

「さらに将来的には新しいシナリオを効率的に作成していくために、既存シナリオをベースにした自動化が図れないものか検討中です。具体的には、Google Cloud が 2018 年に発表した自然言語処理モデル『BERT（Bidirectional Encoder Representations from Transformers）』の論文実装を目指しています。これによって、現在はインターネット バンキングに限定されているチャットボット対応を他のコールセンターにも拡げていきたいですね。」（島野さん）




それらの通信のインターフェイスについては、後で問題にならないよう設計の段階で入念に確認を取りつつ進めています。また、将来的にはコールセンター業務に留まらず、グループ全体でさまざまな用途で使えるようにしたかったので、横展開のしやすさも重視し、コードによるインフラの運用管理などにもチャレンジしています。




「三菱UFJ銀行では、Google Cloud をコールセンター業務へのチャットボット導入に利用しています」と教えてくれたのは、
同行デジタル企画部の島野さん。三菱UFJ銀行は、その規模・事業領域の広さゆえにお客さまからの問い合わせも多く、コールセンター宛に毎月大量の問い合わせ電話がかかってきているのだそうです。

「デジタル企画部ではデジタライゼーション戦略の一環として、ここに発生しているコストをデジタル技術を駆使することで削減できないかというプロジェクトを 2018 年に立ち上げました。
お客さまからのお問い合わせを Web から受けて、まずはチャットボットが対応、回答できない場合はオペレーターに繋ぐというかたちで電話の件数を減らしていこうという取り組みです。まずは手始めに、個人情報を取り扱わず定型対応しやすいインターネット バンキング「三菱UFJダイレクト」に関するコールセンター業務に導入し、
2020 年 1 月時点で約 2 万 7,000 件／月のお問い合わせにチャットボットが対応しています。」


（デジタル企画部 島野さん）



事例：

https://cloud.google.com/blog/ja/topics/customers/mufj-dialogflow

株式会社三菱UFJ銀行：お客様向けコールセンター業務のチャットボット化に Dialogflow を導入


例えば、AI・機械学習は限られたリソースで複雑なビジネス課題を解く上で、的確に膨大なデータを処理できる有効なツールであり、Google Cloud の AI ソリューションも幅広い業界業種のお客様の課題解決に活用されています。株式会社三菱 UFJ 銀行では、Google Cloud のチャットボット向け AI ソリューション「 Dialogflow 」を導入し、2020 年 1 月時点で「三菱 UFJ ダイレクト」に寄せられる約 2 万 7,000 件／月のお問い合わせにチャットボットが対応し、現場の負担軽減や業務効率化が進められています。




https://japan.zdnet.com/paper/30001001/30004104/
コールセンター業務のチャットボット化はGoogle Cloudで。三菱UFJ銀行の構造改革


https://cloud.google.com/blog/ja/topics/customers/g-suite-yokohama

https://workspace.google.co.jp/intl/ja/customers/yokohama.html


横浜ゴム株式会社の導入事例：働き方改革の実現に向け、G Suite への全面移行を決意

これからの時代のスピード感についていけないのではないか。そんな危機感から、2017 年に G Suite の徹底活用を決意した横浜ゴム株式会社。G Suite のさまざまな機能を活用することで、業務の効率はどれほど向上したのか。Google サイトを活用した社内マニュアルの公開や、Dialogflow を利用した社内チャットボットによるヘルプデスク負荷低減の運用など、その成果を、同社 情報企画グループ グループリーダーの時田 健嗣さんに伺ったインタビュー動画をご覧ください。



https://cloud.google.com/blog/ja/products/gcp/introducing-dialogflow-enterprise-edition-a-new-way-to-build-voice-and-text-conversational-apps


https://cloud.google.com/blog/ja/products/gcp/introducing-dialogflow-enterprise-edition-a-new-way-to-build-voice-and-text-conversational-apps



ユニクロ、PolicyBazaar.com、ストレイヤー大学などの企業や組織は、すでに Dialogflow を使って会話エクスペリエンスを設計し、デプロイしています。
ユニクロの新しいショッピング体験に活用

ユニクロは、全世界で 約 1,900 店舗を展開する日本の先進的なアパレル小売ブランドです。同社ではモバイル アプリにチャットボットを搭載し、オンライン上だけでなく店舗でも、お客様のさまざまな質問に対応しています。現在、一部の会員向けにサービスを提供しており、ショッピングをより楽しく、シンプルにするこのチャットボットは、ユーザーの 40 % が毎週利用しています。

「私たちのショッピング チャットボットは Dialogflow を使って開発しました。メッセージング インターフェースを通じて、新しいショッピング体験を提供するとともに、お客様とのやり取りを機械学習によって継続的に改善しています。将来的には音声認識への拡張や多言語展開も検討しています。」
― 松山　真哉氏、ユニクロ　グローバル デジタル コマース部 ディレクター​


保険商品の買い方を変える PolicyBazaar.com

PolicyBazaar.com は、インドの主要な保険商品向けマーケットプレイスです。消費者の啓蒙に加え、保険商品の比較や購入を容易にすることを目的に 2008 年に設立されました。現在、PolicyBazaar.com の年間訪問者数は 8,000 万人を超え、月間取引件数は 15 万件近くに達しています。




https://www.slideshare.net/takashisuzuki503/gree-dialogflow-86672074

[Gree] Dialogflowを利用したチャットボット導入事例





https://xtech.nikkei.com/atcl/nxt/column/18/01688/071300009/
https://internet.watch.impress.co.jp/docs/news/1313663.html
損保ジャパンが取り組む「まず電話」からの脱却、Google Chat利用率は90％以上に




FAQシステムは会話形式でアクセス、前田建設がチャットUIの導入を進める理由




Dialogflow - https://dialogflow.com/

Amazon Lex - https://aws.amazon.com/lex/

IBM Watson Assistant - https://www.ibm.com/cloud/watson-assistant/

Wit.ai - https://wit.ai/

Azure Bot Service - https://azure.microsoft.com/en-us/services/bot-service/








ヤマハ株式会社


https://cloud.google.com/blog/ja/topics/customers/yamaha-adopting-speech-to-text-as-the-voice-recognition-technology-for-communication-robots

世界初の歌によるコミュニケーション ロボットの音声認識技術に Speech-to-Text を採用


金融サービス
金融サービス業ほど、管理が必要な情報が日常的に発生する業界はめずらしいでしょう。市場変化の分析であれ、不正行為やマネー ロンダリングなどの金融犯罪の防止であれ、パーソナライズされた保険プランの提供であれ、ビジネスの成功にはデータを理解してすぐに適切な分析情報を得ることが非常に重要です。Google は、Citi、Two Sigma、KeyBank などの金融サービス業のお客様と長期間連携して、それらのお客様が急速に変化するグローバル市場に適応し、競争力を維持できるようサポートしてきました。たとえば、HSBC では AI でより早く正確に不正行為を検出する方法を模索しています。多くの金融機関は、カスタマー エクスペリエンスへのインテリジェンスの付加に機械学習ツールが役立つことを実感しています。優れたチャットボットやインテリジェントなケースルーティングに加えて、請求書や契約書の処理を効率化するためのドキュメント理解機能を、独自の機械学習モデルを構築することなく利用できます。




利用者数：

2017年11月18日

https://techcrunch.com/2017/11/16/google-launches-an-enterprise-edition-of-its-dialogflow-chatbot-tool/



https://jp.techcrunch.com/2017/11/18/2017-11-16-google-launches-an-enterprise-edition-of-its-dialogflow-chatbot-tool/?guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvLmpwLw&guce_referrer_sig=AQAAAEM3vs2NUO50jpRjO2iykxKfUcnEmRAFCdhH0S_As9XsqWotagfSX_SLA_dbLjQ6xmRh94CYVkmc0wlTekqXxhOArNyUGI58AEskEQKyZyDDQVY0JH2wet4GeR76C4tn3t9oFLCIUSTtBPvS4di0ZaD1qgr0F1HBrfzQWQ-mklXz


GoogleがAPI.AIを買収したとき、それはすでに、チャットボット作成ツールとして相当人気が高かった。そしてGoogleによると、その勢いは今だに衰えていない。GoogleのPRはAharonに、人気第一位のツールとは言うな、と釘をさしたらしいが、実際に人気一位であっても意外ではない。彼によると、無料バージョンだけの現状で登録ユーザー数（デベロッパー数）は“数十万”、今年のCloud Nextイベントを共有したデベロッパー数が15万だから、それよりずっと多いのは確実だ。


When Google acquired API.AI, it was already one of the most popular tools for building chatbots and Google argues that this momentum has only continued. Google PR told Aharon not to say that it’s the most popular tool of its kind on the market, but chances are it actually is. He told me that the service now has now signed up “hundreds of thousands” of developers — and definitely far more than the 150,000 developers number the company shared at its Cloud Next event earlier this year.


https://www.youtube.com/dialogflow?app=desktop&uid=1EXoqvR9VrmWnM9S47SfVA&hl=ja


https://www.youtube.com/watch?v=27OYulL_jdk



https://www.youtube.com/watch?v=27OYulL_jdk


###### tags: `chatbot`