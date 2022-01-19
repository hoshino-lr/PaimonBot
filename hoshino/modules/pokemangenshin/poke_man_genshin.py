import math, random, base64
from PIL import Image, ImageFont, ImageDraw
import pandas as pd
import hoshino
from hoshino import Service, util
from hoshino.modules.Genshin_Impact_games import chara, _Genshin_Impact_data
from hoshino.typing import MessageSegment, NoticeSession, CQEvent
from . import *
from ...util import FreqLimiter
from io import BytesIO

not_poke = False
__BASE = os.path.split(os.path.realpath(__file__))
FRAME_DIR_PATH = os.path.join(__BASE[0], 'image')
DIR_PATH = os.path.join(os.path.expanduser(hoshino.config.RES_DIR), 'Genshin_Impact_icon')
DB_PATH = os.path.expanduser("~/.hoshino/poke_man_genshin.db")
BD_PATH = os.path.expanduser("~/.hoshino/poke_baodi_genshin.npz")  # 保底
POKE_GET_CARDS = 1  # 每一戳的卡片掉落几率
POKE_DAILY_LIMIT = 10  # 机器人每天掉落卡片的次数
RARE_PROBABILITY = 0.10  # 戳一戳获得五星卡片的概率
SUPER_RARE_PROBABILITY = 0.02  # 戳一戳获得超稀有卡片的概率
POKE_TIP_LIMIT = 1  # 到达每日掉落上限后的短时最多提示次数
TIP_CD_LIMIT = 10 * 60  # 每日掉落上限提示冷却时间
POKE_COOLING_TIME = 3  # 增加冷却时间避免连续点击
RESET_HOUR = 0  # 每日戳一戳、赠送等指令使用次数的重置时间，0代表凌晨0点，1代表凌晨1点，以此类推
COL_NUM = 6  # 查看仓库时每行显示的卡片个数
PRELOAD = True  # 是否启动时直接将所有图片加载到内存中以提高查看仓库的速度(增加约几M内存消耗)
sv = Service('poke-man-genshin', bundle='原神娱乐', help_='''
戳一戳机器人, 她可能会送你公主连结卡片哦~
查看仓库 [@某人](这是可选参数): 查看某人的卡片仓库和收集度排名，不加参数默认查看自己的仓库
'''.strip())
poke_tip_cd_limiter = FreqLimiter(TIP_CD_LIMIT)
daily_tip_limiter = DailyAmountLimiter(POKE_TIP_LIMIT, RESET_HOUR)
daily_limiter = DailyAmountLimiter(POKE_DAILY_LIMIT, RESET_HOUR)
cooling_time_limiter = FreqLimiter(POKE_COOLING_TIME)
db = CardRecordDAO(DB_PATH)
font = ImageFont.truetype('arial.ttf', 16)
card_ids = []
card_file_names_all = []
star2rarity = {'4': -1, '5': 0, '6': 1}  # 角色头像星级->卡片稀有度
cards = {'4': [], '5': [], '6': []}  # 4,5,6表示不同星级的角色头像
chara_ids = {'4': [], '5': [], '6': []}

# 资源预检
image_cache = {}
image_list = os.listdir(DIR_PATH)
for image in image_list:
    if not image.startswith('1'):
        continue
    # 图像缓存
    if PRELOAD:
        image_path = os.path.join(DIR_PATH, image)
        image_cache[image] = Image.open(image_path)
    chara_id = int(image[0:3])
    if chara_id not in _Genshin_Impact_data.CHARA_NAME and chara_id != 100:
        continue
    star = image[3]
    cards[star].append(image)
    chara_ids[star].append(chara_id)
    card_ids.append(chara_id)
    card_file_names_all.append(image)
# 边框缓存
frame_names = ['superiorsuperrare.png', 'rare.png', 'superrare.png']
frames = {}
frames_aplha = {}
for frame_name in frame_names:
    frame = Image.open(FRAME_DIR_PATH + f'/{frame_name}')
    frame = frame.resize((80, 80), Image.ANTIALIAS)
    r, g, b, a = frame.split()
    frames[frame_name] = frame
    frames_aplha[frame_name] = a


def get_pic(pic_path, card_num, rarity):
    if PRELOAD:
        # 拆分路径和文件名
        pic_name = os.path.split(pic_path)[1]
        img = image_cache[pic_name]
    else:
        img = Image.open(pic_path)
    img = img.resize((80, 80), Image.ANTIALIAS)
    return draw_num_text(add_rarity_frame(img, rarity), card_num, True, (0, 0, 0), 0, 0)


def get_grey_pic(pic_path, rarity):
    if PRELOAD:
        # 拆分路径和文件名
        pic_name = os.path.split(pic_path)[1]
        img = image_cache[pic_name]
    else:
        img = Image.open(pic_path)
    img = img.resize((80, 80), Image.ANTIALIAS)
    img = add_rarity_frame(img, rarity)
    img = img.convert('L')
    return img


def add_rarity_frame(img, rarity):
    if rarity == 1:
        frame_file_name = frame_names[0]
    elif rarity == 0:
        frame_file_name = frame_names[1]
    else:
        frame_file_name = frame_names[2]
    img.paste(frames[frame_file_name], (0, 0), mask=frames_aplha[frame_file_name])
    return img


def add_card_amount(img, card_amount):
    quantity_base = Image.open(FRAME_DIR_PATH + '/quantity.png')
    img.paste(quantity_base, (53, 54), mask=quantity_base.split()[3])
    return draw_num_text(img, card_amount, False, (255, 255, 255), 2, 1)


def add_icon(base, icon_name, x, y):
    icon = Image.open(FRAME_DIR_PATH + f'/{icon_name}')
    base.paste(icon, (x, y), mask=icon.split()[3])
    return base


def draw_num_text(img, num, draw_base_color, color, offset_x, offset_y):
    draw = ImageDraw.Draw(img)
    n = num if num < 100 else num
    text = f'×{n}'
    if len(text) == 2:
        offset_r = 0
        offset_t = 0
    else:
        offset_r = 10
        offset_t = 9
    if draw_base_color:
        draw.rectangle((59 - offset_r, 60, 75, 77), fill=(255, 255, 255))
        draw.rectangle((59 - offset_r, 60, 77, 75), fill=(255, 255, 255))
    draw.text((60 - offset_t + offset_x, 60 + offset_y), text, fill=color, font=font)
    return img


def get_random_cards_list(groupid, uid):
    cards_list = []
    card = []
    if db.get_gacha_num(groupid, uid)[0] >= 9:
        r = random.random()
        if r > 0.10:
            cards_list = cards['5']
        else:
            cards_list = cards['6']
        card = random.choice(cards_list)
        db.add_delete_num(groupid, uid)
    else:
        r = random.random()
        if 0.5 > r > 0.5 - SUPER_RARE_PROBABILITY:
            cards_list = cards['6']
            db.add_delete_num(groupid, uid)
        elif 0.5 < r < 0.5 + RARE_PROBABILITY:
            cards_list = cards['5']
            db.add_delete_num(groupid, uid)
        else:
            cards_list = cards['4']
            db.add_gacha_num(groupid, uid)
        card = random.choice(cards_list)
    while int(card[0:3]) in _Genshin_Impact_data.UNUSE_NAME:
        card = random.choice(cards_list)
    return card


def get_random_cards(origin_cards, groupid, uid, card_file_names_list=card_file_names_all, amount=10, bonus=True):
    card_ids = []
    size = 80
    margin = 7
    margin_offset_x = 6
    margin_offset_y = 6
    col_num = math.ceil(amount / 2)
    row_num = 2 if amount != 1 else 1
    cards_amount = []
    for i in range(amount):
        a = roll_extra_bonus() if bonus else 1
        cards_amount.append(a)
    offset_y = 0
    offset_critical_strike = 0
    size_x, size_y = (col_num * size + (col_num + 1) * margin + 2 * margin_offset_x,
                      offset_y + row_num * size + (row_num + 1) * margin + 2 * margin_offset_y + offset_critical_strike)
    base = Image.new('RGBA', (size_x, size_y), (255, 255, 255, 255))
    frame = Image.open(FRAME_DIR_PATH + '/background.png')
    frame = frame.resize((size_x, size_y - offset_y), Image.ANTIALIAS)
    base.paste(frame, (0, offset_y), mask=frame.split()[3])
    card_counter = {}
    card_descs = []
    rarity_desc = {1: '六星', 0: '五星', -1: '四星'}
    for i in range(amount):
        random_card = get_random_cards_list(groupid, uid)
        card_id, rarity = get_card_id_by_file_name(random_card)
        card_amount = cards_amount[i]
        card_counter[card_id] = card_amount
        new_string = ' 【NEW】' if card_id not in origin_cards else ''
        if db.get_card_num(groupid, uid, card_id) > 7:
            new_string = ' 已转化'
        card_desc = f'{rarity_desc[rarity]}「{get_chara_name(card_id, rarity)[1]}」×{card_amount}{new_string}'
        card_descs.append(card_desc)
        if PRELOAD:
            img = image_cache[random_card]
        else:
            img = Image.open(DIR_PATH + f'/{random_card}')
        row_index = i // col_num
        col_index = i % col_num
        img = img.resize((size, size), Image.ANTIALIAS)
        img = add_rarity_frame(img, rarity)
        if card_amount > 1:
            img = add_card_amount(img, card_amount)
        coor_x, coor_y = (margin + margin_offset_x + col_index * (size + margin),
                          margin + margin_offset_y + offset_y + offset_critical_strike + row_index * (size + margin))
        base.paste(img, (coor_x, coor_y))
        if card_id not in origin_cards:
            base = add_icon(base, 'new.png', coor_x + size - 27, coor_y - 5)
    return card_counter, card_descs, MessageSegment.image(util.pic2b64(base))


# 输入'[稀有度前缀][角色昵称]'格式的卡片名, 例如'黑猫','稀有黑猫','超稀有黑猫', 输出角色昵称标准化后的结果如'「凯露」','稀有「凯露」','超稀有「凯露」'
def get_card_name_with_rarity(card_name):
    if card_name.startswith('六星'):
        chara_suffix = card_name[0:2]
        chara_nickname = card_name[3:]
    elif card_name.startswith('五星'):
        chara_suffix = card_name[0:2]
        chara_nickname = card_name[2:]
    else:
        chara_suffix = '四星'
        chara_nickname = card_name[2:] if card_name.startswith('四星') else card_name
    chara_name = chara.fromname(chara_nickname).name
    return f'{chara_suffix}「{chara_name}」'


# 由卡片id(形如3xxxx)提取稀有度前缀和角色名
def get_chara_name(card_id, rarity):
    chara_id = card_id
    if rarity == 1:
        rarity_desc = '【六星】的'
    elif rarity == 0:
        rarity_desc = '【五星】的'
    else:
        rarity_desc = '【四星】的'
    return rarity_desc, chara.fromid(chara_id).name


# 由'[稀有度前缀][角色昵称]'格式的卡片名, 返回卡片id(形如3xxxx)，如果卡片不存在则返回0
def get_card_id_by_card_name(card_name):
    if card_name.startswith('六星'):
        rarity = 1
        star = '6'
        chara_name_no_prefix = card_name[3:]
    elif card_name.startswith('五星'):
        rarity = 0
        star = '5'
        chara_name_no_prefix = card_name[2:]
    else:
        rarity = -1
        star = '4'
        chara_name_no_prefix = card_name[2:] if card_name.startswith('四星') else card_name
    chara_id = chara.name2id(chara_name_no_prefix)
    return (30000 + rarity * 1000 + chara_id) if chara_id != chara.UNKNOWN and chara_id in chara_ids[star] else 0


# 单次戳机器人获得的卡片数量
def roll_cards_amount():
    CARDS_EVERY_POKE = 1
    return CARDS_EVERY_POKE


def roll_extra_bonus():
    amount = 1
    return amount


def get_card_id_by_file_name(image_file_name):
    chara_id = int(image_file_name[0:3])
    rarity = star2rarity[image_file_name[3]]
    return chara_id, rarity


def get_card_rarity(card_id):
    if card_id in chara_ids['6']:
        return 1
    elif card_id in chara_ids['5']:
        return 0
    else:
        return -1


def normalize_digit_format(n):
    return f'0{n}' if n < 10 else f'{n}'


def trans_card(uid, gid):
    cards_num = db.get_cards_num(gid, uid)
    cards_num = {card_id: card_amount for card_id, card_amount in cards_num.items() if card_id in card_ids}
    for num in cards_num.keys():
        if num == 100:
            continue
        if cards_num[num] > 7:
            if num in chara_ids['6']:
                multi = 25
            elif num in chara_ids['5']:
                multi = 5
            else:
                multi = 1
            db.change_card_num(uid, gid, num)
            db.add_card_num(gid, uid, 100, multi * (cards_num[num] - 7))


@sv.on_notice('notify.poke')
async def poke_back(session: NoticeSession):
    if not_poke:
        await session.send(f'今天不能抽卡捏')
    else:
        uid = session.ctx['user_id']
        at_user = MessageSegment.at(session.ctx['user_id'])
        guid = session.ctx['group_id'], session.ctx['user_id']
        if not cooling_time_limiter.check(uid):
            return
        cooling_time_limiter.start_cd(uid)
        if session.ctx['target_id'] != session.event.self_id:
            return
        if not daily_limiter.check(guid) and not daily_tip_limiter.check(guid):
            poke_tip_cd_limiter.start_cd(guid)
        if not daily_limiter.check(guid) and poke_tip_cd_limiter.check(guid):
            daily_tip_limiter.increase(guid)
            await session.send(f'{at_user}你今天戳得已经够多的啦，再戳派蒙就不高兴了')
            return
        daily_tip_limiter.reset(guid)
        if not daily_limiter.check(guid) or random.random() > POKE_GET_CARDS:
            poke = MessageSegment(type_='poke',
                                  data={
                                      'qq': str(session.ctx['user_id']),
                                  })
            await session.send(poke)
        else:
            card_counter, card_descs, card = get_random_cards(
                db.get_cards_num(session.ctx['group_id'], session.ctx['user_id']), session.ctx['group_id'],
                session.ctx['user_id'], card_file_names_all,
                roll_cards_amount(), True)
            dash = '----------------------------------------'
            msg_part = '\n'.join(card_descs)
            num = db.get_gacha_num(session.ctx['group_id'], session.ctx['user_id'])[0]
            num = 10 - num
            await session.send(f'{card}{at_user}这些卡送给你了\n{dash}\n获得了:\n{msg_part}\n离保底还有{num}抽\n')
            for card_id in card_counter.keys():
                db.add_card_num(session.ctx['group_id'], session.ctx['user_id'], card_id, card_counter[card_id])
            daily_limiter.increase(guid)


@sv.on_prefix('查看原神仓库')
async def storage(bot, ev: CQEvent):
    if len(ev.message) == 1 and ev.message[0].type == 'text' and not ev.message[0].data['text']:
        uid = ev.user_id
    elif ev.message[0].type == 'at':
        uid = int(ev.message[0].data['qq'])
    else:
        await bot.finish(ev, '参数格式错误, 请重试')
    row_nums = {}
    for star in cards.keys():
        row_nums[star] = math.ceil(len(cards[star]) / COL_NUM)
    row_num = sum(row_nums.values())
    base = Image.open(FRAME_DIR_PATH + '/frame.png')
    base = base.resize((40 + COL_NUM * 80 + (COL_NUM - 1) * 10, 120 + row_num * 80 + (row_num - 1) * 10),
                       Image.ANTIALIAS)
    trans_card(uid, ev.group_id)
    cards_num = db.get_cards_num(ev.group_id, uid)
    cards_num = {card_id: card_amount for card_id, card_amount in cards_num.items() if card_id in card_ids}
    row_index_offset = 0
    row_offset = 0
    for star in cards.keys():
        cards_list = cards[star]
        for index, id in enumerate(cards_list):
            row_index = index // COL_NUM + row_index_offset
            col_index = index % COL_NUM
            card_id, rarity = get_card_id_by_file_name(cards_list[index])
            pic_path = DIR_PATH + f'/{cards_list[index]}'
            f = get_pic(pic_path, cards_num[card_id], rarity) if card_id in cards_num else get_grey_pic(pic_path,
                                                                                                        rarity)
            base.paste(f, (
                30 + col_index * 80 + (col_index - 1) * 10, row_offset + 40 + row_index * 80 + (row_index - 1) * 10))
        row_index_offset += row_nums[star]
        row_offset += 30
    ranking = db.get_group_ranking(ev.group_id, uid)
    ranking_desc = f'第{ranking}位' if ranking != -1 else '未上榜'
    total_card_num = sum(cards_num.values())
    super_rare_card_num = len([card_id for card_id in cards_num if get_card_rarity(card_id) == 1])
    super_rare_card_total = len(cards['6'])
    rare_card_num = len([card_id for card_id in cards_num if get_card_rarity(card_id) == 0])
    rare_card_total = len(cards['5'])
    normal_card_num = len(cards_num) - super_rare_card_num - rare_card_num
    normal_card_total = len(cards['4'])
    buf = BytesIO()
    base = base.convert('RGB')
    base.save(buf, format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'

    lr_card = cards_num[100] if 100 in cards_num else 0

    await bot.send(ev,
                   f'{MessageSegment.at(uid)}的仓库:[CQ:image,file={base64_str}]\n四星卡收集: {normalize_digit_format(normal_card_num)}/{normalize_digit_format(normal_card_total)}\n'
                   f'五星卡收集: {normalize_digit_format(rare_card_num)}/{normalize_digit_format(rare_card_total)}\n'
                   f'六星卡收集: {normalize_digit_format(super_rare_card_num)}/{normalize_digit_format(super_rare_card_total)}\n'
                   f'小红帽碎片持有数: {normalize_digit_format(lr_card)}\n'
                   f'当前群排名: {ranking_desc}')


@sv.on_fullmatch('转换碎片')
async def send_card(bot, ev: CQEvent):
    uid = ev.user_id
    if uid == 1786944781:
        uids = db.get_uids(ev.group_id).keys()
        for item in uids:
            trans_card(uid, ev.group_id)
        await bot.send(ev, f'转换成功')



@sv.on_keyword('补偿')
async def send_card(bot, ev: CQEvent):
    text = str(ev.message).strip().split(" ")
    if ev.user_id != hoshino.config.SUPERUSERS[0]:
        await bot.send("您没有补偿权限捏")
    elif len(text) == 4:
        lim2 = bool(len(text) == 4)
        lim1 = bool(text[0] == "补偿")
        lim3 = bool(int(text[2]) in _Genshin_Impact_data.CHARA_NAME.keys())
        lim4 = bool(int(text[3]))
        if lim1 and lim2 and lim3 and lim4:
            await bot.send(ev, "补偿成功捏")
            db.add_card_num(str(665601009), text[1], int(text[2]), int(text[3]))
            message = f'补偿消息\n本次补偿内容为{_Genshin_Impact_data.CHARA_NAME[int(text[2])][0]}x{text[3]}'
            await bot.send_private_msg(self_id=ev.self_id, user_id=text[1], message=f'补偿成功\n{message}')
        else:
            await bot.send(ev, "补偿格式不正确捏")
