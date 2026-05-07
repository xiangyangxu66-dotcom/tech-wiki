# rasa env - zh




```
sudo apt install -y \
build-essential \
libffi-dev \
libssl-dev \
zlib1g-dev \
liblzma-dev \
libbz2-dev \
libreadline-dev \
libsqlite3-dev \
libopencv-dev \
tk-dev \
git



# pyenv本体のダウンロードとインストール
git clone https://github.com/pyenv/pyenv.git ~/.pyenv

# (Option)pyenvのバージョンをv2.0.3に変更
cd ~/.pynev
git checkout v2.0.3

# .bashrcの更新
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
source ~/.bashrc


 pyenv versions
 
pyenv install 3.8.6

# pyenv global 3.8.6

# pyenv local 3.8.6 (任意のディレクトリで実行)

 
```


> curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
> git clone https://github.com/RasaHQ/rasa.git
> cd rasa
> poetry install
> 
> 



1. Pipeline

rasa nlu 支持不同的 Pipeline，其后端实现可支持spaCy、MITIE、MITIE + sklearn 以及 tensorflow，其中 spaCy 是官方推荐的，另外值得注意的是从 0.12 版本后，MITIE 就被列入 Deprecated 了。

本例使用的 pipeline 为 MITIE+Jieba+sklearn， rasa nlu 的配置文件为 config_jieba_mitie_sklearn.yml如下：
```

language: "zh"

pipeline:
- name: "nlp_mitie"
  model: "data/total_word_feature_extractor_zh.dat"  // 加载 mitie 模型
- name: "tokenizer_jieba"   // 使用 jieba 进行分词
- name: "ner_mitie"   // mitie 的命名实体识别
- name: "ner_synonyms"
- name: "intent_entity_featurizer_regex"
- name: "intent_featurizer_mitie"  // 特征提取
- name: "intent_classifier_sklearn" // sklearn 的意图分类模型

```

###### tags: `chatbot`