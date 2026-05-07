# 典型Pipeline



* 初始化组件：加载模型文件，为后续组件提供框架支持，如初始化Spacy和MITIE；

* 分词组件：将文本分割成词语序列，为后续的高级 NLP 任务提供基础数据；

* 提取特征组件：提取词语序列文本特征，通常采用Word Embedding的方式，提取特征的组件可以同时使用，同时搭配的还可能有基于正则表达式的提取特征方法。

* NER组件：根据前面提供的特征，对文本进行命名实体识别；

* 意图分类组件：按照语义对文本进行意图分类，也称意图识别。


1. 初始化组件

目前只有两个初始化组件：nlp_spacy和nlp_mitie，分别对应 SpaCy和MITIE。

基于MITIE的组件，如： tokenizer_mitie、intent_featurizer_mitie、ner_mitie和intent_classifier_mitie都将依赖nlp_mitie 提供的对象。

基于SpaCy的组件，如：tokenizer_spacy、intent_featurizer_spacy和ner_spacy都将依赖nlp_spacy提供的对象。

2. 分词组件

Rasa分词组件中，tokenizer_jieba支持中文分词，tokenizer_mitie经过改造可以支持中文分词，tokenizer_spacy暂不支持中文分词但未来会支持（需要跟进）。

3. 提取特征组件

命名实体识别和意图分类，都需要上游组件提供特征。常见特征有：词向量、Bag-of-words、N-grams、正则表达式。用户可以同时使用多个组件提取特征，这些组件在实现层面上做了合并特性的操作。

4. NER组件

- ner_crf
  使用CRF模型来做ENR,CRF模型只依赖tokens本身，如果想在feature function中使用POS特性，那么则需要nlp_spacy组件提供spacy_doc对象，来提供POS信息。

- ner_mitie

  利用MITIE模型提供的language model，只需要tokens就可以进行NER。

- ner_spacy

  利用SpaCy模型自带的NER功能，模型的训练需要在SpaCy框架下进行，当前SpaCy不支持用户训练自己的模型，而SpaCy官方的模型只支持常见的几种实体，具体情况见官方文档。（某大神说 spacy已经支持自定义实体，spacy中文模型地址：https://github.com/howl-anderson/Chinese_models_for_SpaCy）

- ner_duckling 
  Duckling是Facebook出品的一款用Haskell语言写成的NER库，基于规则和模型。Duckling对中文的支持并不是很全面，只支持诸多实体类型中的几种。在Rssa中有两种方式去调用Duckling，一种是通过duckling这个包使用wrap的方式访问，另一种是通过HTTP访问。上述两种访问方式分别对应ner_duckling和ner_duckling_http这两个组件。

- ner_synonyms
  正确来说ner_synonyms不是一个命名实体的提取组件，更像是一个归一化的组件。ner_synonyms主要是将各种同义词（synonyms）映射成标准词汇，比如将实体“KFC”映射成“肯德基”，归一化操作为后续业务处理提供便利。



- Pipeline组件特征

  组件之间的顺序很重要，比如NER组件之前要有分词器组件；
  
  组件可替换，比如分词器；
  
  有些组件是互斥的，比如分词器只能有一个；
  
  有些组件可以同时使用，比如提取文本特征的组件可以同时使用基于规则的和基于文本嵌入向量的。

- Pipeline配置选择

Rasa NLU的配置文件使用的是YAML(YAML Ain’t Markup Language)格式，例如：

```
language: "en"
 
pipeline:
  - name: "nlp_mitie"
    model: "data/total_word_feature_extractor.dat"
  - name: "tokenizer_mitie"
  - name: "ner_mitie"
  - name: "ner_synonyms"
  - name: "intent_entity_featurizer_regex"
  - name: "intent_classifier_mitie"
```
Rasa NLU的配置还可以采用预定义的pipeline的方式，例如：

pipeline: tensorflow_embedding
Rasa NLU预定义的pipeline有：tensorflow_embedding、spacy_sklearn。

训练数据少于1000条，用spacy_sklearn的pipline；

训练数据多于1000条，用tensorflow_embedding的pipeline；

配置language参数对于spacy_sklearn是有效的，对于tensorflow_embedding是无效的；

配置位置：nlu_config.yml

spacy_sklearn有预训练的词向量；tensorflow_embedding没有；

- 工具选择

MITIE： 一个包罗万象的库;  换言之，它有一个内置的用于”实体”提取的NLP库，以及一个用于”意图”分类的ML库。

spaCy + sklearn： spaCy是一个只进行”实体”提取的NLP库。而sklearn是与spaCy一起使用的，用于为其添加ML功能来进行”意图”分类操作。

MITIE + sklearn： 该组合使用了两个各自领域里最好的库。该组合既拥有了MITIE中良好的”实体”识别能力，又拥有sklearn中的快速和优秀的”意图”分类。

在小的训练集合中进行实验时，MITIE比spaCy + sklearn更精确，但是随着”意图”集合的不断增加，MITIE的训练过程变得越来越慢。




###### tags: `chatbot`