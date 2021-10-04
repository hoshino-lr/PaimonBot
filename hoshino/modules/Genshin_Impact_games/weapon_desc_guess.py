import asyncio
import os
import random

from hoshino import Service
from hoshino.modules.Genshin_Impact_games import chara
from hoshino.typing import CQEvent, MessageSegment as Seg

from . import _Genshin_Impact_data
from . import GameMaster

weapon_sesc_DEBUG = True
PREPARE_TIME = 8
ONE_TURN_TIME = 5
TURN_NUMBER = 4
DB_PATH = os.path.expanduser("~/.hoshino/Genshin_weapon_desc_guess.db")
NOT_USE = [132, 134]
gm = GameMaster(DB_PATH)
sv = Service("Genshin-weapon-desc-guess", bundle="原神娱乐", help_="""
[猜原神角色] 猜猜bot在描述哪位角色
[猜原神角色排行] 显示小游戏的群排行榜(只显示前十)
""".strip()
)


@sv.on_fullmatch(("原神猜武器排名", "原神猜武器排行榜", "原神猜武器群排行"))
async def description_guess_group_ranking(bot, ev: CQEvent):
    ranking = gm.db.get_ranking(ev.group_id)
    msg = ["【原神猜武器小游戏排行榜】"]
    for i, item in enumerate(ranking):
        uid, count = item
        m = await bot.get_group_member_info(self_id=ev.self_id, group_id=ev.group_id, user_id=uid)
        name = m["card"] or m["nickname"] or str(uid)
        msg.append(f"第{i + 1}名：{name} 猜对{count}次")
    await bot.send(ev, "\n".join(msg))


@sv.on_fullmatch("原神猜武器")
async def description_guess(bot, ev: CQEvent):
    global weapon_sesc_DEBUG
    if weapon_sesc_DEBUG:
        await bot.send(ev, f"此小游戏暂不开放呢\n")
    else:
        if gm.is_playing(ev.group_id):
            await bot.finish(ev, "游戏仍在进行中…")
        with gm.start_game(ev.group_id) as game:
            game.answer = random.choice(list(_Genshin_Impact_data.WEAPON_PROFILE.keys()))
            while game.answer in NOT_USE:
                game.answer = random.choice(list(_Genshin_Impact_data.WEAPON_PROFILE.keys()))
            profile = _Genshin_Impact_data.WEAPON_PROFILE[game.answer]
            kws = list(profile.keys())
            kws.remove("名字")
            random.shuffle(kws)
            await bot.send(ev, f"{PREPARE_TIME}秒后每隔{ONE_TURN_TIME}秒我会给出某个武器的一个描述，根据这些描述猜猜TA是谁~")
            await asyncio.sleep(PREPARE_TIME)
            for i, k in enumerate(kws):
                await bot.send(ev, f"提示{i + 1}/{len(kws)}:\nTA的{k}是 {profile[k]}")
                await asyncio.sleep(ONE_TURN_TIME)
                if game.winner:
                    return
            c = chara.fromid(game.answer)
        await bot.send(ev, f"正确答案是：{c.name} {c.icon.cqcode}\n")


@sv.on_message()
async def on_input_chara_name(bot, ev: CQEvent):
    game = gm.get_game(ev.group_id)
    if not game or game.winner:
        return
    c = chara.fromname(ev.message.extract_plain_text())
    if c.id != chara.UNKNOWN and c.id == game.answer:
        game.winner = ev.user_id
        n = game.record()
        msg = f"正确答案是：{c.name}{c.icon.cqcode}\n{Seg.at(ev.user_id)}猜对了，真厉害！\n(此轮游戏将在几秒后自动结束，请耐心等待)"
        await bot.send(ev, msg)
