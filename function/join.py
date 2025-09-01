import discord

class VCJoinView(discord.ui.View):
  def __init__(self, vcs: list[discord.VoiceChannel]):
    super().__init__(timeout=60)  # 1分で操作終了
    # ボタンは最大25個まで（5x5）
    for vc in vcs[:25]:
      self.add_item(JoinVCButton(vc))

class JoinVCButton(discord.ui.Button):
  def __init__(self, vc: discord.VoiceChannel):
    super().__init__(label=vc.name, style=discord.ButtonStyle.primary, custom_id=f"join:{vc.id}")
    self.vc_id = vc.id

  async def callback(self, interaction: discord.Interaction):
    guild = interaction.guild
    assert guild is not None

    target_vc = guild.get_channel(self.vc_id)
    if not isinstance(target_vc, discord.VoiceChannel):
      return await interaction.response.send_message("チャンネルがみつからないよ！", ephemeral=True)

    # 押した時点で空いてるか最初に確認
    if len(target_vc.members) != 0:
      await interaction.response.send_message(
        f"ごめん、`{target_vc.name}`にはもうすでに誰かが入っているみたい。再度`empty_vc`を実行して別チャンネルに参加してね。",
        ephemeral=True,
        delete_after=10
      )
      await refresh_empty_vc_buttons(interaction)
      return

    member = interaction.user if isinstance(interaction.user, discord.Member) else await guild.fetch_member(interaction.user.id)

    # もう一度直前で再確認（移動/招待直前の二重チェック）
    if len(target_vc.members) != 0:
      await interaction.response.send_message(
        f"直前に埋まっちゃった…`{target_vc.name}` はもう使用中。",
        ephemeral=True,
        delete_after=10
      )
      await refresh_empty_vc_buttons(interaction)
      return

    # 既にどこかのVCにいるなら移動、いなければ招待
    if member.voice and member.voice.channel:
      perms = target_vc.permissions_for(guild.me)
      if not perms.move_members:
        return await interaction.response.send_message(
          "僕に『メンバーを移動』の権限が要るの。",
          ephemeral=True,
          delete_after=10
        )
      try:
        await member.move_to(target_vc)
        await interaction.response.send_message(
          f"`{target_vc.name}` に移動させたよ。",
          ephemeral=True,
          delete_after=30)
      except discord.Forbidden:
        await interaction.response.send_message(
          "権限が足りないみたい。Move Members / Connect を確認して。",
          ephemeral=True,
          delete_after=10)
      except Exception as e:
        await interaction.response.send_message(
          f"移動できなかった…: {e}",
          ephemeral=True,
          delete_after=10)
    else:
      perms = target_vc.permissions_for(guild.me)
      if not perms.create_instant_invite:
        return await interaction.response.send_message(
          "招待を作る権限（Create Invite）が無い。付けて！",
          ephemeral=True,
          delete_after=10)
      invite = await target_vc.create_invite(max_age=300, max_uses=1, unique=True)
      await interaction.response.send_message(
        f"`{target_vc.name}` に入るならここ → {invite.url}（5分で失効）",
        ephemeral=True,
        delete_after=300
      )

    await refresh_empty_vc_buttons(interaction)

async def refresh_empty_vc_buttons(interaction: discord.Interaction, limit: int = 5):
  guild = interaction.guild
  if guild is None or interaction.message is None:
    return
  empty_channels = [vc for vc in guild.voice_channels if len(vc.members) == 0][:limit]
  if not empty_channels:
    try:
      await interaction.message.edit(
        content="今は空いてるVCは無いよ。新規作成してね。",
        view=None)
    except Exception:
      pass
      return
  try:
    await interaction.message.edit(view=VCJoinView(empty_channels))
  except Exception:
    pass
