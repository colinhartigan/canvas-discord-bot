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

def oneUserMeetLinks(links,date,name="someone's",color=discord.Colour.green()):
    embed = discord.Embed(
        title = "{}'s google meet links for {}".format(name,date),
        color = color,
    )
    for i in links:
        embed.add_field(
            name = "pd {}/ {}".format(i[1][-1],i[0]),
            value = "[{}](http://g.co/meet/{})".format(i[1],i[1]),
            inline = False
        )
    return embed

def allMeetLinks(codes,date,color=discord.Color.green()):
    payload = []
    for index,period in enumerate(codes):
        embed = discord.Embed(
            title = "all meet links for period {} on {}".format(index+1,date),
            color = color,
        )
        for i in period:
            embed.add_field(
                name = "{} pd {}".format(i[0],i[1][-1]),
                value = "[{}](http://g.co/meet/{})".format(i[1],i[1]),
                inline = False
            )
        payload.append(embed)
    return payload

def courseOnboarding(course):
    embed = discord.Embed(
        title = course.name,
        description = "react with the period you have this course, or ❌ if this is not a regular course",
        color = discord.Color.from_rgb(226,43,39)
    )
    return embed