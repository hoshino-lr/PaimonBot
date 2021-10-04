import asyncio
import os
import random

from hoshino import Service, util
from hoshino.typing import CQEvent
from hoshino.typing import MessageSegment as Seg
from . import Love_master

DB_PATH = os.path.expanduser("~/.hoshino/Paimon_love.db")
Paimon_love = Love_master(DB_PATH)
sv = Service(
    "Paimon-love-guess", bundle="原神娱乐", help_="""
派蒙好感度捏
""".strip()
)

love_names = ["永远不会分开", "陪伴之上的爱慕", "形影不离的两人", "最好的伙伴", "默契的伙伴", "伙伴", "向导", "陌生人"]


async def send_upgrate(bot, ev: CQEvent, gid, uid, c_after):
    message = f"和派蒙的关系上升了，现在的关系为\n{c_after}"
    await bot.send(ev, message)


def love_ranking(love_count):
    love_name = "伙伴"
    if love_count > 30:
        love_name = love_names[4]
    if love_count > 60:
        love_name = love_names[3]
    if love_count > 90:
        love_name = love_names[2]
    if love_count > 180:
        love_name = love_names[1]
    if love_count > 365:
        love_name = love_names[0]

    if love_count < 0:
        love_name = love_names[-2]
    if love_count < -30:
        love_name = love_names[-1]
    return love_name


@sv.on_fullmatch("派蒙好感度排行")
async def description_guess_group_ranking(bot, ev: CQEvent):
    ranking = Paimon_love.db.get_ranking(ev.group_id)
    msg = ["【派蒙好感度排行】"]
    for i, item in enumerate(ranking):
        uid, count = item
        m = await bot.get_group_member_info(
            self_id=ev.self_id, group_id=ev.group_id, user_id=uid
        )
        name = m["card"] or m["nickname"] or str(uid)
        msg.append(f"第{i + 1}名：{name}")
    await bot.send(ev, "\n".join(msg))


@sv.on_fullmatch(("派蒙好感度", "好感度"))
async def get_love(bot, ev: CQEvent):
    count = Paimon_love.db.get_love_count(ev.group_id, ev.user_id)
    CLASS = love_ranking(count)
    await bot.send(ev, f"旅行者和派蒙的关系是：\n{CLASS}")
