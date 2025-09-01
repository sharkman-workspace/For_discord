import discord
import config
from discord.ext import commands
from discord import app_commands
from function.join import VCJoinView

# オブジェクト生成
intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 起動時に動作する処理
@bot.event
async def on_ready():
  # ターミナルにログイン通知
  print('ログインしました')
  synced = await bot.tree.sync()
  print(f"グローバル同期したコマンド数: {len(synced)}")

##### 空いているvcを表示して参加を促すコマンド #####
@bot.tree.command(name="empty_vc", description="空いてるVCをボタン付きで表示(最大5個)")
async def empty_vc(interaction: discord.Interaction):
  # 空きVCを集める（0人のみ）
  empty_channels = [vc for vc in interaction.guild.voice_channels if len(vc.members) == 0]

  if not empty_channels:
    return await interaction.response.send_message("今は空いてるVCは無いよ。新規作成してね。", ephemeral=True)

  # ボタン出力
  view = VCJoinView(empty_channels[:5])
  await interaction.response.send_message(
    "空いてるVC一覧（押したら参加/移動）",
    view=view,
    ephemeral=True,
    delete_after=30
  )

##### 番号を入力して、近い名前のvcチャンネルを表示するコマンド #####
async def vc_autocomplete(
  interaction: discord.Interaction,
  current: str
) -> list[app_commands.Choice[str]]:
  guild = interaction.guild
  if guild is None:
    return []

  # 入力に部分一致するVC最大25件を候補に（表示名は名前、値はID文字列）
  vchs = []
  for vc in guild.voice_channels:
    if current.lower() in vc.name.lower():
      # 似た名前が複数あってもIDで一意に選べる
      vchs.append(app_commands.Choice(name=vc.name, value=str(vc.id)))
      if len(vchs) >= 25:
        break
  # 何も入力してないときは上位25件
  if not current and not vchs:
    vchs = [app_commands.Choice(name=vc.name, value=str(vc.id))
    for vc in guild.voice_channels[:25]]
  return vchs

@bot.tree.command(name="join_vc", description="VC名を指定してそのVCへ移動（待機VCに入ってる前提）")
@app_commands.describe(vc="行きたいボイスチャンネル名を選んでね")
@app_commands.autocomplete(vc=vc_autocomplete)
async def join_vc(interaction: discord.Interaction, vc: str):
  guild = interaction.guild
  if guild is None:
    return await interaction.response.send_message("ギルドが取れない…", ephemeral=True, delete_after=6)

  # ユーザー（Member）取得
  member = interaction.user
  if not isinstance(member, discord.Member):
    member = await guild.fetch_member(interaction.user.id)

  # まずあなたがどこかのVCに入ってるか確認（“待機VC前提”だけど一応ガード）
  if not (member.voice and member.voice.channel):
    return await interaction.response.send_message(
      "先に待機VCに入ってから呼びなおして。", ephemeral=True, delete_after=6
    )

  # オートコンプリートの value は VCのID文字列
  try:
    target_id = int(vc)
  except ValueError:
    return await interaction.response.send_message("VCの指定が不正だよ。候補から選び直して。", ephemeral=True, delete_after=6)

  target = guild.get_channel(target_id)
  if not isinstance(target, discord.VoiceChannel):
    return await interaction.response.send_message("そのVCが見つからないよ。", ephemeral=True, delete_after=6)

  # 移動に必要な権限チェック（Bot側）
  bot_member = guild.me or await guild.fetch_member(bot.user.id)
  perms = target.permissions_for(bot_member)
  if not (perms.move_members and perms.connect):
    return await interaction.response.send_message(
      "僕に『メンバーを移動』と『接続』の権限を付けて。", ephemeral=True, delete_after=8
    )

  # いざ移動（満員・接続不可などは例外で拾う）
  try:
    await member.move_to(target)
    await interaction.response.send_message(
      f"`{target.name}` に移動させたよ！", ephemeral=True, delete_after=5
    )
  except discord.Forbidden:
    await interaction.response.send_message(
      "満員か権限不足で移動できなかったよ。チャンネルの上限や権限を見直して。", ephemeral=True, delete_after=8
    )
  except discord.HTTPException as e:
    await interaction.response.send_message(
      f"移動に失敗した…: {e}", ephemeral=True, delete_after=8
    )

# Botの起動とDiscordサーバーへの接続
bot.run(config.DISCORD_TOKEN)
