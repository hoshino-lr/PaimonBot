import asyncio
import os
import random
from hoshino.modules.Paimon_love.love import Paimon_love
from hoshino import Service, util
from hoshino.modules.Genshin_Impact_games import _Genshin_Impact_data, chara
from hoshino.typing import CQEvent
from hoshino.typing import MessageSegment as Seg
from hoshino import R
from . import GameMaster
from datetime import datetime, date
from collections import Counter

setu_DEBUG = False
PATCH_SIZE = 300
ONE_TURN_TIME = 18
DELETE_AFTER = 19
DB_PATH = os.path.expanduser("~/.hoshino/Genshin_Impact_setu_guess.db")
BLACKLIST_ID = [1072, 1908, 4031, 9000]
gm = GameMaster(DB_PATH)
sv = Service(
    "Genshin-Impact-setu-guess",
    bundle="原神娱乐",
    help_="""
[派蒙猜色图] 猜猜bot随机发送的头像的一小部分来自哪位角色
[派蒙猜色图] 显示小游戏的群排行榜(只显示前十)
""".strip()
)


@sv.on_fullmatch(("派蒙猜色图排行", "派蒙猜色图排行榜", "派蒙猜色图群排行"))
async def description_guess_group_ranking(bot, ev: CQEvent):
    ranking = gm.db.get_ranking(ev.group_id)
    msg = ["【派蒙猜色图排行榜】"]
    for i, item in enumerate(ranking):
        uid, count = item
        m = await bot.get_group_member_info(
            self_id=ev.self_id, group_id=ev.group_id, user_id=uid
        )
        name = m["card"] or m["nickname"] or str(uid)
        msg.append(f"第{i + 1}名：{name} 猜对{count}次")
    await bot.send(ev, "\n".join(msg))


@sv.on_fullmatch(("派蒙猜色图", "猜色图"))
async def avatar_guess(bot, ev: CQEvent):
    global setu_DEBUG
    if setu_DEBUG:
        await bot.send(ev, f"此小游戏暂不开放呢\n")
    else:
        if gm.is_playing(ev.group_id):
            await bot.finish(ev, "游戏仍在进行中…")
        with gm.start_game(ev.group_id) as game:
            game.start_time = datetime.now()
            ids = list(_Genshin_Impact_data.SETU_NAME.keys())
            game.answer = random.choice(ids)
            res = R.img(f'genshin_setu/{game.answer}.jpg')
            if not res.exist:
                res = R.img(f'genshin_setu/{game.answer}.png')
            img = res.open()
            w, h = img.size
            l = random.randint(int(0.3 * w), int(0.5 * w))
            u = random.randint(int(0.3 * h), h - PATCH_SIZE)
            cropped = img.crop((l, u, l + PATCH_SIZE, u + PATCH_SIZE))
            cropped = Seg.image(util.pic2b64(cropped))
            await bot.send(ev, f"猜猜这个图片是哪位角色色图的一部分?({ONE_TURN_TIME}s后公布答案)")
            await bot.send(ev, f"{cropped}")
            await asyncio.sleep(ONE_TURN_TIME)
            if game.winner:
                return
        answer = ""
        for i in _Genshin_Impact_data.SETU_NAME[game.answer]:
            answer += i
            answer += ","
        await bot.send(ev, f"正确答案是：{answer}\n很遗憾，没有人答对~(色图将在{DELETE_AFTER}秒钟后撤回)")
        ret = await bot.send(ev, f" {res.cqcode}")
        msg_id = ret['message_id']
        self_id = ev['self_id']
        await asyncio.sleep(DELETE_AFTER)
        await bot.delete_msg(elf_id=self_id, message_id=msg_id)


@sv.on_message()
async def on_input_chara_name(bot, ev: CQEvent):
    game = gm.get_game(ev.group_id)
    if not game or game.winner:
        return
    if (datetime.now() - game.start_time).seconds < 3:
        return
    name = util.normalize_str(ev.message.extract_plain_text())
    if name in _Genshin_Impact_data.SETU_NAME[game.answer]:
        game.winner = ev.user_id
        n = game.record()
        res = R.img(f'genshin_setu/{game.answer}.jpg')
        if not res.exist:
            res = R.img(f'genshin_setu/{game.answer}.png')
        if random.random() > 0.8:
            await Paimon_love.get_record(bot,ev,ev.group_id,ev.user_id,2)
            msg = f"正确答案是：{_Genshin_Impact_data.SETU_NAME[game.answer]}" \
                  f"{res.cqcode}\n{Seg.at(ev.user_id)}(派蒙好感度增加)"
        else:
            msg = f"正确答案是：{_Genshin_Impact_data.SETU_NAME[game.answer]}{res.cqcode}\n{Seg.at(ev.user_id)}"
        ret = await bot.send(ev, msg)
        msg_id = ret['message_id']
        self_id = ev['self_id']
        await asyncio.sleep(DELETE_AFTER)
        await bot.delete_msg(self_id=self_id, message_id=msg_id)


@sv.on_fullmatch("派蒙色图库")
async def setu_cards(bot, ev: CQEvent):
    setu_names = []
    for item in _Genshin_Impact_data.SETU_NAME.keys():
        for name in _Genshin_Impact_data.SETU_NAME[item]:
            setu_names.append(name)
    collection_words = Counter(setu_names)
    top_5 = collection_words.most_common(5)
    await bot.send(ev, f"{top_5[0][0]}:{top_5[0][1]}张\n"
                       f"{top_5[1][0]}:{top_5[1][1]}张\n"
                       f"{top_5[2][0]}:{top_5[2][1]}张\n"
                       f"{top_5[3][0]}:{top_5[3][1]}张\n"
                       f"{top_5[4][0]}:{top_5[4][1]}张\n"
                       f"一共{len(_Genshin_Impact_data.SETU_NAME.keys())}张\n")
