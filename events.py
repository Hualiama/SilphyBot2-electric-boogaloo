import slog
import discord

async def gate_check(bot: SilphyBot, message: discord.Message):
    if not bot.gate_password:
        return

    if message.content.strip().lower() == bot.gate_password.lower():
        member_role = message.guild.get_role(bot.member_role_id)
        if member_role:
            await message.author.add_roles(member_role)
            slog.info(f"User {message.author.display_name} passed the gate!")
        else:
            slog.warning("Member role not found!")
    else:
        slog.warning(f"User {message.author.display_name} failed the gate check.")
