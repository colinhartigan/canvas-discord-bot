import discord

def errorEmbed(errors):
    embed = discord.Embed(
        title = "error",
        color = discord.Colour.from_rgb(255,0,0),
    )
    for i in errors:
        embed.add_field(
            name=i,
            value=errors[i]
        )
    return embed

def genericSuccess(message,color=discord.Colour.green()):
    embed = discord.Embed(
        title = "success!",
        description = message,
        color = color,
    )
    return embed

def onePeriodMeetLinks(links,date,name="someone's",color=discord.Colour.green()):
    embed = discord.Embed(
        title = "{}'s google meet links for {}".format(name,date),
        color = color,
    )
    for i in links:
        embed.add_field(
            name = "{} pd {}".format(i[0],i[1][-1]),
            value = "[{}](http://g.co/meet/{})".format(i[1],i[1])
        )
    return embed