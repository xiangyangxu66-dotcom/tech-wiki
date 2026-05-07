     1|# BPMと外部システム連携
     2|[toc]
     3|
     4|選択肢がいくつかがあります。「RabbitMQ」と「Flowableメッセージイベント」を紹介します。
     5|
     6|- RabbitMQからのメッセージ
     7|
     8|  RabbitMQはメッセージキューのソフトウェアで、アプリケーション間の非同期通信や分散アーキテクチャをサポートします。RabbitMQからのメッセージは、システム内の別のコンポーネントやサービスからの非同期通信に対応して、Flowableプロセスを開始または制御するために使用されます。これにより、アプリケーション全体の負荷分散や遅延の軽減が可能になります。
     9|
    10|  RabbitMQからのメッセージを使用する場合、通常はSpring IntegrationやApache Camelなどの統合フレームワークと一緒に使います。これにより、メッセージキューからのイベントを受信してプロセスを開始したり、進行中のプロセスに影響を与えたりすることができます。
    11|
    12|- メッセージイベント
    13|
    14|  Flowableのメッセージイベントは、BPMNプロセス内で外部からのメッセージを待ち受けるために使用されます。メッセージイベントは、プロセスの開始イベント、中間キャッチイベント、境界イベントなどとして使用できます。メッセージイベントは、プロセス間の通信やコラボレーションに使用されることが一般的です。
    15|
    16|
    17|## 使い分け
    18|
    19|  RabbitMQからのメッセージは、アプリケーション全体で分散型アーキテクチャをサポートし、非同期通信が必要な場合に適しています。一方、メッセージイベントは、プロセス内で外部からのメッセージを待ち受けるために使用されます。
    20|
    21|  RabbitMQを使用する場合、アプリケーションの他の部分との統合が必要で、Spring IntegrationやApache Camelなどの統合フレームワークが役立ちます。一方、メッセージイベントは、BPMNプロセス内で定義され、FlowableのRuntimeServiceを使用して制御されます。
    22|
    23|  RabbitMQは、システム全体でメッセージの受け渡しを行うために使用されますが、メッセージイベントは、プロセス間のコラボレーションや通信に特化しています。
    24|
    25|
    26|- RabbitMQからのメッセージを使用する場合の例:
    27|
    28|  アプリケーションがマイクロサービスアーキテクチャで構築されており、複数のサービス間で非同期通信が必要な場合。外部システムとの統合が必要で、その外部システムからのイベントやメッセージを受信して、BPMNプロセスを開始または制御する必要がある場合。
    29|
    30|- メッセージイベントを使用する場合の例:
    31|
    32|  2つのプロセスが相互にコラボレーションを行い、あるプロセスの進行状況に応じて別のプロセスを制御する必要がある場合。ワークフロー内で特定の状況が発生したときに、別のプロセスインスタンスに通知する必要がある場合。
    33|
    34|まとめると、RabbitMQからのメッセージはアプリケーション全体で非同期通信を実現するために適しており、メッセージイベントはプロセス間のコラボレーションや通信に特化しています。システムの要件やアーキテクチャに応じて、適切な方法を選択することが重要です。
    35|
    36|
    37|
    38|## 実装方法
    39|
    40|### RabbitMQの取り込み、利用
    41|
    42|1. pomファイル
    43|
    44|```xml
    45|
    46|<!-- Spring Integration -->
    47|<dependency>
    48|  <groupId>org.springframework.integration</groupId>
    49|  <artifactId>spring-integration-core</artifactId>
    50|</dependency>
    51|
    52|<dependency>
    53|  <groupId>org.springframework.integration</groupId>
    54|  <artifactId>spring-integration-amqp</artifactId>
    55|</dependency>
    56|
    57|<!-- RabbitMQ -->
    58|<dependency>
    59|  <groupId>com.rabbitmq</groupId>
    60|  <artifactId>amqp-client</artifactId>
    61|</dependency>
    62|```
    63|
    64|2. application.properties:
    65|
    66|```
    67|# RabbitMQ
    68|spring.rabbitmq.host=localhost
    69|spring.rabbitmq.port=5672
    70|spring.rabbitmq.username=guest
    71|spring.rabbitmq.password=guest
    72|transfer-result.rabbitmq.queue=transfer-result-queue
    73|transfer-result.rabbitmq.exchange=transfer-result-exchange
    74|transfer-result.rabbitmq.routingkey=transfer-result-routingkey
    75|
    76|```
    77|
    78|
    79|3. ダミーデータの定義
    80|
    81|```
    82|public class TransferResultMessage {
    83|    private String messageType;
    84|    private int recordId;
    85|    private String status;
    86|    private List<String> productList;
    87|
    88|    // Getters and setters
    89|}
    90|
    91|```
    92|
    93|4. 送信
    94|
    95|```java
    96|import org.springframework.amqp.rabbit.core.RabbitTemplate;
    97|import org.springframework.beans.factory.annotation.Autowired;
    98|import org.springframework.beans.factory.annotation.Value;
    99|import org.springframework.stereotype.Service;
   100|
   101|@Service
   102|public class TransferPublisher {
   103|
   104|    @Autowired
   105|    private RabbitTemplate rabbitTemplate;
   106|
   107|    @Value("${transfer-result.rabbitmq.exchange}")
   108|    private String exchange;
   109|
   110|    @Value("${transfer-result.rabbitmq.routingkey}")
   111|    private String routingKey;
   112|
   113|    public void publishTransferResult(TransferResultMessage transferResultMessage) {
   114|        rabbitTemplate.convertAndSend(exchange, routingKey, transferResultMessage);
   115|    }
   116|}
   117|
   118|```
   119|
   120|
   121|5. 受信処理
   122|
   123|```java
   124|import org.flowable.engine.ProcessEngine;
   125|import org.springframework.amqp.rabbit.annotation.RabbitListener;
   126|import org.springframework.beans.factory.annotation.Autowired;
   127|import org.springframework.stereotype.Component;
   128|
   129|@Component
   130|public class TransferResultReceiver {
   131|
   132|    @Autowired
   133|    private ProcessEngine processEngine;
   134|
   135|    @RabbitListener(queues = "${transfer-result.rabbitmq.queue}")
   136|    public void receive(TransferResultMessage transferResultMessage) {
   137|        String messageType = transferResultMessage.getMessageType();
   138|        String businessKey = String.valueOf(transferResultMessage.getRecordId());
   139|
   140|        processEngine.getRuntimeService().correlateMessage(messageType, businessKey);
   141|    }
   142|}
   143|
   144|
   145|```
   146|
   147|6. サンプルBPMN
   148|
   149|```xml
   150|<?xml version="1.0" encoding="UTF-8"?>
   151|<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
   152|  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   153|  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
   154|  xmlns:flowable="http://flowable.org/bpmn"
   155|  targetNamespace="http://www.flowable.org/examples">
   156|  
   157|  <process id="sampleProcess" name="Sample Process" isExecutable="true">
   158|    
   159|    <startEvent id="start" flowable:initiator="initiator">
   160|      <messageEventDefinition messageRef="transferResultMessage" />
   161|    </startEvent>
   162|
   163|    <sequenceFlow id="flow1" sourceRef="start" targetRef="task" />
   164|
   165|    <userTask id="task" name="User Task" />
   166|
   167|    <
   168|
   169|```
   170|
   171|
   172|### Flowableのメッセージイベント版
   173|
   174|- ダミーデータ
   175|```java
   176|import java.io.Serializable;
   177|import java.util.List;
   178|
   179|public class TransferData implements Serializable {
   180|    private String messageType;
   181|    private Long recordId;
   182|    private String status;
   183|    private List<String> productList;
   184|
   185|    // コンストラクタ、ゲッター、セッターをここに追加
   186|}
   187|
   188|```
   189|
   190|- Flowableのメッセージイベントをトリガーするためのサービスクラス
   191|
   192|```java
   193|import org.flowable.engine.RuntimeService;
   194|import org.flowable.engine.runtime.ProcessInstance;
   195|import org.springframework.beans.factory.annotation.Autowired;
   196|import org.springframework.stereotype.Service;
   197|
   198|@Service
   199|public class TransferService {
   200|
   201|    @Autowired
   202|    private RuntimeService runtimeService;
   203|
   204|    public void triggerMessageEvent(TransferData transferData) {
   205|        String messageType = transferData.getMessageType();
   206|        String businessKey = String.valueOf(transferData.getRecordId());
   207|
   208|        // メッセージイベントをトリガーします。
   209|        ProcessInstance processInstance = runtimeService
   210|                .createMessageCorrelation(messageType)
   211|                .processInstanceBusinessKey(businessKey)
   212|                .setVariable("status", transferData.getStatus())
   213|                .setVariable("productList", transferData.getProductList())
   214|                .correlateStartMessage();
   215|
   216|        // プロセスインスタンスIDを出力します（デバッグ用）
   217|        System.out.println("Started process instance with ID: " + processInstance.getProcessInstanceId());
   218|    }
   219|}
   220|
   221|- BPMNプロセスでメッセージイベントを定義
   222|
   223|```xml
   224|<bpmn:message id="transferResultMessage" name="TransferResult" />
   225|
   226|<bpmn:process id="myProcess" isExecutable="true">
   227|    <bpmn:startEvent id="startEvent">
   228|        <bpmn:messageEventDefinition messageRef="transferResultMessage" />
   229|    </bpmn:startEvent>
   230|    <!-- 他のタスクやゲートウェイを定義 -->
   231|</bpmn:process>
   232|```
   233|
   234|
   235|

###### tags: `bpm` `flowable` `rabbitmq`
