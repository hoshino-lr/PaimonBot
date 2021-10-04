import os
import sqlite3

class Love_class:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS love_record "
                "(gid INT NOT NULL, uid INT NOT NULL, count INT NOT NULL, PRIMARY KEY(gid, uid))"
            )

    def get_love_count(self, gid, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT count FROM love_record WHERE gid=? AND uid=?", (gid, uid)
            ).fetchone()
            return r[0] if r else 0

    def record_love(self, gid, uid, num=1):
        n = self.get_love_count(gid, uid)
        n += num
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO love_record (gid, uid, count) VALUES (?, ?, ?)",
                (gid, uid, n),
            )
        return n

    def get_ranking(self, gid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT uid, count FROM love_record WHERE gid=? ORDER BY count DESC LIMIT 5",
                (gid,),
            ).fetchall()
            return r


class Love_master:
    def __init__(self, db_path):
        self.db = Love_class(db_path)

    async def get_record(self, bot, ev, gid, uid, num=1):
        from .love import love_ranking,send_upgrate
        n_after = self.db.record_love(gid, uid, num)
        n_before = n_after - num
        c_before = love_ranking(n_before)
        c_after = love_ranking(n_after)
        if c_after != c_before and n_after > n_before:
            await send_upgrate(bot, ev , gid, uid, c_after)
        else:
            pass

