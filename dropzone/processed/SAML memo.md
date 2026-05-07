# SAML memo



■ saml to cognito azuredb 
　→ 仕組み
　→ 使い方
 
　→ 業務での…
 


● AWS Cognito ユーザプール構築
　・　ユーザプール　　
　・　ドメイン名

● AWS AppClient構築、ユーザプール連携
　・　アプリクライアントID
　・　アプリクライアントシークレット
　・　コールバックURL: http://localhost:8080 (動作確認用)
　・　許可されているOAuthフロー: Authorization code grant, Implicit grant
　・　許可されているOAuthのスコープ: email, openId, aws.cognito.signin.user.admin 

● AWS Cognito ユーザプールIdP設定
　・　AzureADからのフェデレーションメタデータにより、IDプロバイダーを作成する
　・　アプリの統合のアプリクライアントの設定にて、上記のIDプロバイダーを設定し連携させる




![](https://i.imgur.com/XG951uj.png)




## 使い方

参照：

https://qiita.com/ksukenobe/items/a80e0e4435bcddd5e379
https://techblog.forgevision.com/entry/2020/07/09/223457
https://qiita.com/kei1-dev/items/a0870c26da51dbaa6580
https://qiita.com/ksukenobe/items/a80e0e4435bcddd5e379
https://aws.amazon.com/jp/premiumsupport/knowledge-center/cognito-ad-fs-saml/


### 関連設定

#### AzureADでSAML設定

Azure Active Directory >> エンタープライズアプリケーションを選択し、New applicationをクリックします。

ギャラリー以外のアプリケーションを選択し、アプリケーションをAddします。

作成したアプリケーションのシングルサインオンを選択し、SAMLをクリックします。

基本的なSAML構成の編集アイコンをクリックして、以下を入力します。
識別子のフォーマット: urn:amazon:cognito:sp:UserPoolID
応答URLのフォーマット: https://yourDomainPrefix.auth.yourRegion.amazoncognito.com/saml2/idpresponse


SAML署名証明書で、アプリのフェデレーション メタデータURLをコピーしておきます。

アプリを利用するユーザをアサインします。







#### CognitoコンソールからIdP設定



AWS Cognitoコンソールからユーザープールを選択します。
フェデレーション >> IDプロバイダー >> SAMLを選択して、プロバイダーを作成します。メタデータドキュメントは、先ほどコピーしたAzure ADのメタデータURLをセットします。


属性マッピングで、Emailを設定します。
SAML属性は、以下を設定します。
http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress



アプリ統合 >> アプリクライアントの設定を選択して、有効な ID プロバイダをAzure ADにします。





#### AmplifyでUserPoolを設定

  amplifyコマンドを実行して、UserPoolを設定します。
  いったんおためしなので、リダイレクトURLはlocalhostにしました。設定後、amplify pushしておきます。

  ```
    $ amplify add auth
    (省略）
     Do you want to use an OAuth flow? Yes
     What domain name prefix you want us to create for you? saml-app-login
     Enter your redirect signin URI: http://localhost:8080/
    ? Do you want to add another redirect signin URI No
     Enter your redirect signout URI: http://localhost:8080/
    ? Do you want to add another redirect signout URI No
     Select the OAuth flows enabled for this project. Authorization code grant
     Select the OAuth scopes enabled for this project. Email, OpenID, Profile, aws.cognito.signin.user.admin
     Select the social providers you want to configure for your user pool: 
    ? Do you want to configure Lambda Triggers for Cognito? No
    Successfully added resource auth locally
    
  ```


### 利用のシーン

　　Azure ADとCognito間がSAML、Cognitoとアプリ間がOAuthという間柄になります。
  
  
  ![](https://i.imgur.com/MSSrR1x.png)


- 動かしてみる

ここまでで、認証基盤の設定は完了です。以下のURLを叩くと、動作確認できます。
https://your_domain/login?response_type=code&client_id=your_app_client_id&redirect_uri=your_callback_url







## SAML認証仕組み


### SAMLとは

SAMLは、Security Assertion Markup Languageの略で読み方は「サムル」です。SAMLとは、OASISによって策定された、異なるインターネットドメイン間でユーザー認証を行うための認証情報の規格です。つまり、ユーザーの認証情報をやり取りするルール・プロトコルを指しています。ちなみにSAML 2.0は、2005年にリリースされたバージョン2.0のSAMLです。


### 仕組み

SAMLを使った認証では、次のような流れで進みます。SAMLは、IdPとSPが情報をやり取りする際に、情報の形式や書式を変換する作業を省きます。

![](https://i.imgur.com/8qUKGBY.png)


#### ユーザーとは

ユーザーとは、SPと称されるクラウドサービスへログインしたい人をさします。たとえば、SalesforceやOneDriveへログインしたい方がこのユーザーに該当します。

#### SPとは

SPとは、Service Providerの略でログインされるクラウドサービスをさします。SalesforceやOneDrice以外にも多くのクラウドサービスが存在しますが、これらクラウドサービス全般がこのSPに該当します。

#### IdPとは

IdPとは、Identify Providerの略で認証情報を提供するシステムです。SPへログインしようと試みているユーザーが、以前登録したユーザーであるか確認し、結果をSPへ送ります。具体的なサービスの例は、OneLoginやトラスト・ログインです。

#### 認証の流れ

![](https://i.imgur.com/p8KngsJ.png)


1. ユーザーはログインするためにSPへアクセスします
1. SPはSAML認証要求を作成します
1. SPはユーザーのアクセスをSAML認証要求とあわせてIdPへ送ります
1. IdPはSAML認証要求を受け取って、適切なユーザーであるか確認します
1. IdPはSAML認証応答を作成します。SAML認証応答には、SPへログインしたいユーザーが登録されているものか認証します
1. SPは受け取ったSAML認証応答にもとづいて、ユーザーのログインを許可／拒否します




### SAMLとSSO

SAMLは、SSO（シングルサインオン）を実現するために必要不可欠な仕組みです。SSOは、1つのIDとパスワードで一度認証を行うことで、複数のWebサービスやクラウドサービスにアクセスする仕組みのことをいいます。サービスが多様化している時代に、ユーザーの手間を省くために普及してきたサービスです。

SSOを利用するためには、それぞれのサービスに共通した型を準備する必要があります。SAMLは、その型そのものを表していて、ユーザーを認証するシステムと各サービスの認証システムをつなぐ橋ということができます。



### SAMLとOAuthの違い

SAMLとOAuthは、SAMLが認証するためのシステムであるのに対しに、OAuthは認可するためのシステムであるという違いがあります。誤解を恐れずにいえば、認証とはユーザーが登録されているアカウントと一致するか確かめること、認可とはアカウントを登録することです。

OAuthはユーザーの情報を登録、SAMLはログイン時にユーザー情報をチェックという点で両者は異なります。ちなみにOpenID Connectは、SAMLと似た技術で場面やサービスによって使い分けがなされます。




---

---
---





SAML認証の処理のフロー


---


![](https://i.imgur.com/I6hdaLN.png)




![](https://i.imgur.com/OrRn3cT.png)






## 用語

**SAML**

---

- IdP Initiated SSO	
 
  SPからの認証リクエストを受け取らずにIdPがユーザの認証を開始し、認証後にIdPがSPにSAMLレスポンスを渡してシングルサインオンを行うことです

- IdPメタデータ	

  IdPに関する情報を含んだXMLファイルです。SPがIdPメタデータによってSAML連携が設定できる場合、IIJ IDサービスが提供するIdPメタデータを利用できます

- SAML

  (Security Assertion Markup Language)

   異なるドメイン間でユーザ認証情報を交換できるXMLベースの標準規格です。
   

- SAML IdP (Identity Provider)	

  ユーザの認証を行い、SPに認証情報を提供するエンティティです

- SAML SP (Service Provider)	

  ユーザにサービスを提供するエンティティです

- SAML属性ステートメント

  (SAML Attribute Statement)
  SAMLレスポンスに含まれる特有の識別情報です

- SP Initiated SSO	

  SPがSAMLリクエストをIdPに渡してユーザの認証を開始し、認証後にIdPがSPにSAMLレスポンスを渡してシングルサインオンを行うことです

- SPメタデータ	
- 
  SPに関する情報を含んだXMLファイルです。SPがSPメタデータを提供している場合、IIJ IDサービスでのアプリケーション登録にSPメタデータを利用できます

- SSOエンドポイントURL	
  SPからIdPにSAMLリクエストを行う場合にアクセスするURLです
  
  
- エンティティID (Entity ID)	
   エンティティを一意に識別するIDです

<br><br><br>

**OpenID Connect**

---

- Authorization Code Flow	

   RPがOPからIDトークンを受け取るフローの一つです。OPは認可コードを認可リクエスト時に指定されたリダイレクトURLに付与して、RPに受け渡します。RPは認可コードをOPに提示することで、IDトークンを取得します


- Authorizationエンドポイント(autorhization_endpoint)	

  ユーザの認証を行なうエンドポイントです


- Discoveryエンドポイント	Discovery情報を提供するエンドポイントです

- Discovery情報	OPが提供するエンドポイントや、対応する署名アルゴリズムなどの情報です

- IDトークン	認証についてのクレームを含んだJSON Webトークン(JWT)

- Implicit Flow	
   RPがOPからIDトークンを受け取るフローの一つです。OPはIDトークンを認可リクエスト時に指定されたリダイレクトURLに付与して、RPに受け渡します

- issuer	IDトークンの発行元です

- JSON Web Key Set
   暗号鍵を表すJSONデータ(JWK)の集合です

- OP（OpenID Provider）	
   OpenID Connect規格に対応した、認証を実際に実施するサーバです

- OpenID Connect	
   OAuth 2.0をベースとする、シンプルなアイデンティティ連携プロトコルのことです。IIJ IDサービスは、OpenID Connect Core 1.0をサポートします

- RP（Relaying Party）	
   OpenID Connectを利用して利用者を認証し、利用者にサービスを提供するアプリケーションです

- Tokenエンドポイント(token_endpoint)
  アクセストークン、IDトークン、またはリフレッシュトークンを取得するためのエンドポイント

- Userinfoエンドポイント(userinfo_endpoint)	
   認証されたユーザに関するクレームを返すエンドポイントです

- アクセストークン
  リソースサーバ上の保護された情報にアクセスするための資格情報となるトークンです


- クライアンID（client_id）
  OPに登録されているRPを識別するためのIDです


- クライアントシークレット（client_secret）
  RPがOPから発行されたIDトークンの署名検証に使用する秘密鍵です

- クレーム(claim)	ユーザの属性情報です


- スコープ（scope）
	認可後にOPからRPに提供される属性情報を指定するための値です

- リダイレクトURL（redirect_uri）
  ログイン後にリダイレクトするURLです


- リフレッシュトークン	
   アクセストークンを更新するためのトークンです


###### tags:  `auth` `saml`






