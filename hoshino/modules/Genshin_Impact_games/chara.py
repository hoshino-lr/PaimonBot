import importlib
from io import BytesIO

import pygtrie
import requests
from fuzzywuzzy import fuzz, process
from PIL import Image

import hoshino
from hoshino import R, log, sucmd, util
from hoshino.typing import CommandSession

from . import _Genshin_Impact_data

logger = log.new_logger('chara', hoshino.config.DEBUG)
UNKNOWN = 100
UnavailableChara = {132}  # 暂时不用


# try:
#     gadget_equip = R.img('priconne/gadget/equip.png').open()
#     gadget_star = R.img('priconne/gadget/star.png').open()
#     gadget_star_dis = R.img('priconne/gadget/star_disabled.png').open()
#     gadget_star_pink = R.img('priconne/gadget/star_pink.png').open()
#     unknown_chara_icon = R.img(f'priconne/unit/icon_unit_{UNKNOWN}31.png').open()
# except Exception as e:
#     logger.exception(e)


class Roster:

    def __init__(self):
        self._roster = pygtrie.CharTrie()
        self.update()

    def update(self):
        importlib.reload(_Genshin_Impact_data)
        self._roster.clear()
        for idx, names in _Genshin_Impact_data.CHARA_NAME.items():
            for n in names:
                n = util.normalize_str(n)
                if n not in self._roster:
                    self._roster[n] = idx
                else:
                    logger.warning(f'Genshin_Impact.chara.Roster: 出现重名{n}于id{idx}与id{self._roster[n]}')
        for idx, names in _Genshin_Impact_data.WEAPON_NAME.items():
            for n in names:
                n = util.normalize_str(n)
                if n not in self._roster:
                    self._roster[n] = idx
                else:
                    logger.warning(f'Genshin_Impact.chara.Roster: 出现重名{n}于id{idx}与id{self._roster[n]}')
        self._all_name_list = self._roster.keys()

    def get_id(self, name):
        name = util.normalize_str(name)
        return self._roster[name] if name in self._roster else UNKNOWN

    def guess_id(self, name):
        """@return: id, name, score"""
        name, score = process.extractOne(name, self._all_name_list, processor=util.normalize_str)
        return self._roster[name], name, score

    def parse_team(self, namestr):
        """@return: List[ids], unknown_namestr"""
        namestr = util.normalize_str(namestr.strip())
        team = []
        unknown = []
        while namestr:
            item = self._roster.longest_prefix(namestr)
            if not item:
                unknown.append(namestr[0])
                namestr = namestr[1:].lstrip()
            else:
                team.append(item.value)
                namestr = namestr[len(item.key):].lstrip()
        return team, ''.join(unknown)


roster = Roster()


def name2id(name):
    return roster.get_id(name)


def fromid(id_):
    return Chara(id_)


def fromname(name):
    id_ = name2id(name)
    return Chara(id_)


def guess_id(name):
    """@return: id, name, score"""
    return roster.guess_id(name)


def is_npc(id_):
    if id_ in UnavailableChara:
        return True
    else:
        # return not (100 < id_ < 140)
        return False

class Chara:

    def __init__(self, id_):
        self.id = id_

    @property
    def name(self):
        if self.id > 1000:
            name = _Genshin_Impact_data.WEAPON_NAME[self.id][0]
        else:
            name = _Genshin_Impact_data.CHARA_NAME[self.id][0]
        return name

    @property
    def is_npc(self) -> bool:
        return is_npc(self.id)

    @property
    def icon(self):
        global res
        if self.id > 1000:
            res = R.img(f'Genshin_weapon_icon/{_Genshin_Impact_data.WEAPON_NAME[self.id][0]}.jpg')
            if not res.exist:
                res = R.img(f'Genshin_weapon_icon/{_Genshin_Impact_data.WEAPON_NAME[self.id][0]}.png')
        else:
            res = R.img(f'Genshin_Impact_icon/{_Genshin_Impact_data.CHARA_NAME[self.id][1]}.jpg')
            if not res.exist:
                res = R.img(f'Genshin_Impact_icon/{_Genshin_Impact_data.CHARA_NAME[self.id][1]}.png')
        return res


@sucmd('reload-Genshin-Impact-chara', force_private=False, aliases=('重载花名册',))
async def reload_pcr_chara(session: CommandSession):
    try:
        roster.update()
        await session.send('ok')
    except Exception as e:
        logger.exception(e)
        await session.send(f'Error: {type(e)}')
