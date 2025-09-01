# Search vc channel
空いているvcチャンネルを探したり、すぐさま参加できるようにします。
## コマンド機能
### `empty_vc`
空いてるvcをボタン付きで表示(最大5個)<br>
すでにvcに参加している場合移動するだけ<br>
まだvcに参加していない場合は招待リンクを踏む必要がある<br>
解決策として待機vcを用意すると円滑に参加できるようになる

### `join_vc`
引数に予測ワードを打ち込むとそれに近いチャンネル名のボイスチャンネルを表示する<br>
実行するとそのボイスチャンネルに参加できるが、すでにボイスチャンネルに参加しておく必要がある<br>
これも`empty_vc`同様待機vcを用意するといいだろう

# 事前準備
こちらのサイトを参考にしながら進めてほしい。
https://qiita.com/shown_it/items/6e7fb7777f45008e0496<br>
他に言うことは何もない

`.env`ファイルの中にDiscordのbotトークン書いて
```txt:.env
DISCORD_TOKEN=tokenの番号
```

## botの設定
OAuth2 URL GeneratorでTEXT PERMISSIONSの
- Send Messages
- Embed Links
- Use Slash Commands

にチェックを入れてボットを動かすこと。権限不足でうまくいかない可能性あり。
