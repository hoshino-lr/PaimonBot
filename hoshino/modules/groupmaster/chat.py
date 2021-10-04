import random
from datetime import timedelta
from nonebot import on_command
from hoshino.modules.Paimon_love.love import Paimon_love
from hoshino import R, Service, priv, util

fuck_sakura_count = 41

# basic function for debug, not included in Service('chat')
@on_command('zai?', aliases=('在?', '在？', '在吗', '在么？', '在嘛', '在嘛？'), only_to_me=True)
async def say_hello(session):
    await session.send('派蒙一直在旅行者身边哦')

sv = Service('chat', visible=False)

@sv.on_fullmatch('朋友', only_to_me=True)
async def say_sorry(bot, ev):
    await bot.send(ev, '派蒙是旅行者最好的伙伴')
    await Paimon_love.get_record(bot, ev, ev.group_id, ev.user_id)


@sv.on_fullmatch(('老婆', 'waifu', 'laopo'), only_to_me=True)
async def chat_waifu(bot, ev):
    await bot.send(ev, '派蒙也喜欢旅行者哦')
    await Paimon_love.record_love(ev.group_id, ev.user_id)


@sv.on_fullmatch('老公', only_to_me=True)
async def chat_laogong(bot, ev):
    await bot.send(ev, '派蒙不是男的！', at_sender=True)


@sv.on_fullmatch('mua', only_to_me=True)
async def chat_mua(bot, ev):
    await bot.send(ev, '旅行者亲一下也不是不可以啦~', at_sender=True)
    await Paimon_love.get_record(bot, ev, ev.group_id, ev.user_id,2)


@sv.on_fullmatch('应急食品')
async def chat_food(bot, ev):
    pic = R.img('food.png').cqcode
    await bot.send(ev, f"派蒙不是应急食品！\n{pic}", at_sender=True)


@sv.on_fullmatch('你能表演一下那个吗', only_to_me=True)
async def chat_(bot, ev):
    await bot.send(ev, '就表演一下哦~', at_sender=True)
    await bot.send(ev, '前面的区域，以后再来探索吧', at_sender=True)


@sv.on_fullmatch(('我有个朋友说他好了', '我朋友说他好了'))
async def ddhaole(bot, ev):
    await bot.send(ev, '那个朋友是不是你？')
    await util.silence(ev, 30)


@sv.on_fullmatch('我好了')
async def nihaole(bot, ev):
    await bot.send(ev, '不许好，憋回去！')
    await util.silence(ev, 30)


# ============================================ #


@sv.on_keyword(('确实', '有一说一', 'u1s1', 'yysy'))
async def chat_queshi(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('确实.jpg').cqcode)


@sv.on_keyword('透sakura')
async def fuck_sakura(bot, ctx):
    global fuck_sakura_count
    fuck_sakura_count += 1


@sv.on_fullmatch('sakura被透次数')
async def sakura_fuck_count(bot, ctx):
    print(f"sakura被透次数累计为{fuck_sakura_count}次")
    await bot.send(ctx, f"sakura被透次数累计为{fuck_sakura_count}次")


@sv.on_keyword('suki', only_to_me=True)
async def chat_mua(bot, ev):
    pic = R.img("dokidoki.jpg").cqcode
    await Paimon_love.get_record(bot, ev, ev.group_id, ev.user_id,4)
    await bot.send(ev, f'派蒙也喜欢旅行者，dokidoki\n{pic}', at_sender=True)


@sv.on_keyword('内鬼')
async def chat_neigui(bot, ctx):
    if random.random() < 0.10:
        await bot.send(ctx, R.img('内鬼.png').cqcode)
