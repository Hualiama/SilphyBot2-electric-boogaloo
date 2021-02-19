import slog
import discord


async def gate_check(bot, message: discord.Message):
	if bot.gate_password == "":
		return
	
	text = message.content
	
	if text.lower() == bot.gate_password.lower():
		member_role = message.guild.get_role(bot.member_role_id)
		await message.author.add_roles(member_role)
		slog.info("User {0} passed the gate!".format(message.author.display_name))
