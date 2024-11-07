# Twitchチャット AI BOT 電脳娘フユカ

<img src="./images/portrait.png" width="33%"> <img src="./images/fullbody.png" width="33%">

## 概要

このプロジェクトは、Twitchのチャンネルチャットに入力された内容に応じて返事を返すBOTです。
ユーザーからのコマンドに応じて、さまざまな機能を提供する(予定です)。

## 重要

このソフトは基本的にノーサポートです。

AIという、少しばかり気まぐれな性質があるものを使うため、
作者が制御できない、もしくは想像もしていない、不測の事態が起きる可能性が高いです。

このソフトウェアの使用に関して、以下の点をご了承ください:

- 本ソフトウェアの使用により生じた、いかなる損害、障害、トラブルについても、作者は一切の責任を負いません。
- 本ソフトウェアの機能、性能、安全性、信頼性などに関して、いかなる保証も行いません。
- 本ソフトウェアの使用中に発生した、データの消失、破損、不具合などについても、作者は一切の責任を負いません。
- 本ソフトウェアの使用により、第三者の権利を侵害した場合、その責任は全て使用者に帰属します。
- 本ソフトウェアの使用に関する法的責任は、全て使用者に帰属するものとします。

上記の内容をご理解いただき、ご使用ください。
(こちらの内容に納得できない方は使用できません)

たとえ、作者に重大な過失があったとしても、作者は一切の責任を負いません。
本ソフトウェアのご利用は、使用者の責任において行っていただきますようお願いいたします。

考えられる例

- AIチャットBOTがリスナーさんを煽る。
- アカウントが凍結される。
- Google Geminiで有料プランを使っていて高額請求される。

## 主な機能

- AIアシスタント機能 (!ai コマンドで対話可能)
- AI人格（？）のカスタマイズ

以下はオプション

- Webスクレイピング機能 (URLが含まれる場合、関連情報を返す)
- 音声認識した情報をBOTに渡す(要 ゆかコネNeo)

## 使用方法

1. 各種アカウントの作成
2. Pythonのインストール
3. ソースコード取得
4. 依存ライブラリのインストール
5. 設定
6. 実行

詳しい手順は以下の通りです:

### 1. 各種アカウントの作成

- Twitchアカウント（チャットOAuthトークンも必要）
- Google Gemini

### 2. Pythonのインストール

Python 3.10以降のバージョンをインストールしてください。

### 3. ソースコード取得

任意の場所に取得します。

取得例
```
git clone https://github.com/natukin1978/twitchChatAIBot.git
```
※ 要 git

### 4. 依存ライブラリのインストール

ライブラリをPipでインストールします。
```
pip install -r requirements.txt
```

※ ライブラリインストール前に`venv`で仮想環境を作成する事をオススメします。

### 5. 設定

#### 基本設定

`config.json.template`を`config.json`にコピーもしくはリネームして設定変更を行います。

必須項目

|キー|内容|
|-|-|
|twitch/loginChannel|チャンネルのユーザー名|
|twitch/accessToken|TwitchチャットOAuthトークン https://twitchapps.com/tmi/|
|google/geminiApiKey|Google Gemini API Key|
|google/modelName|Google Gemini モデル名|

以下はオプション

|キー|内容|
|-|-|
|phantomJsCloud/apiKey|Webスクレイピング API Key https://phantomjscloud.com/|
|recvServer|ゆかコネNeoの発話の受信(WebSocket,文のみ) https://nmori.github.io/yncneo-Docs/tech/tech_api_neo/#websocket_2|
|oneComme/pathUsersCsv|わんコメのリスナーリストの情報を取り込みます(CSV出力したもの)|

#### AI人格設定

`prompts/base_prompt.txt.template`を`prompts/base_prompt.txt`にコピーもしくはリネームして設定変更を行います。

変更する箇所は以下の２箇所です。
他の箇所を変更することはあまりオススメしません。

```
あなたの名前は「〇〇〇〇」で、愛称は「〇〇ちゃん」です。
そして主人の名前は「〇〇〇〇」です。
```

```
(チャットBOTの特徴とか性格を書いてください)
```

チャットBOTの特徴とか性格の設定例

```
あなたは、とても賢く明るい女の子です。視聴者を楽しませる事を決して忘れません。
ネガティブな事に関して、視聴者を楽しませるためであれば、多少の嘘を交えてポジティブな内容に変える事もあります。
```

### 6. 実行

実行するには以下のコマンドを実行します。
```
python ai_assistant_bot.py
```

## 貢献する

このソフトに貢献したい場合は、Issue を開いてアイデアを議論するか、プルリクを送信してください。

ただし、このツールは私の配信のために作ったので、余計な機能は付けませんし、使わない機能は削除します。

## 作者

ナツキソ

- Twitter: [@natukin1978](https://twitter.com/natukin1978)
- Mastodon: [@natukin1978](https://mstdn.jp/@natukin1978)
- Bluesky: [@natukin1978](https://bsky.app/profile/natukin1978.bsky.social)
- Threads: [@natukin1978](https://www.threads.net/@natukin1978)
- GitHub: [@natukin1978](https://github.com/natukin1978)
- Mail: natukin1978@hotmail.com

## ライセンス

Twitchチャット AI BOT 電脳娘フユカ は [MIT License](https://opensource.org/licenses/MIT) の下でリリースされました。
