from mitmproxy import ctx
import math
import os
import random
import re
import sqlite3
import time


class TorrentRatio:
    def __init__(self):
        low = {
            'uploaded': (0.1, 0.6),
            'downloaded': (0, 0.07),
            'percent_min': 0.2,
            'percent_max': 0.5,
            'percent_step': 0.02,
            'speed': 51200
        }
        high = { # noqa
            'uploaded': (2, 4),
            'downloaded': (0.08, 0.1),
            'percent_min': 0.4,
            'percent_max': 0.7,
            'percent_step': 0.06,
            'speed': 102400
        }
        self.setting = {
            'default': low,
            '127.0.0.1': {
                **low,
                'uploaded': (2, 2),
                'downloaded': (1, 1),
                'percent_max': .5
            }
        }
        db_file = os.path.join(os.path.dirname(__file__), 'torrent_ratio.db')
        self.con = sqlite3.connect(db_file)
        self.con.row_factory = sqlite3.Row
        self.con.execute('''CREATE TABLE IF NOT EXISTS torrent
        (info_hash TEXT PRIMARY KEY, host TEXT, report_uploaded INTEGER,
        uploaded INTEGER, downloaded INTEGER, epoch REAL,
        incomplete INTEGER)''')

    def done(self):
        self.con.close()

    def request(self, flow):

        def format(num):
            for unit in ['B', 'K', 'M', 'G']:
                if abs(num) < 1024.0:
                    return '%3.1f%s' % (num, unit)
                num /= 1024.0
            return '%.1f%s' % (num, 'T')

        query = flow.request.query
        info_hash = query['info_hash'].encode('utf-8', 'surrogateescape').hex()
        uploaded = int(query['uploaded'])
        downloaded = int(query['downloaded'])
        host = flow.request.pretty_host
        setting = self.setting['default']
        if host in self.setting:
            setting = self.setting[host]
        epoch = time.time()
        report_uploaded = uploaded
        incomplete = -3
        info = self.con.execute('''SELECT * FROM torrent WHERE info_hash=?''', (info_hash,)).fetchone()
        if ('event' not in query or query['event'] != 'started') and info:
            delta_uploaded = uploaded - info['uploaded']
            delta_downloaded = downloaded - info['downloaded']
            delta_epoch = epoch - info['epoch']
            if delta_uploaded >= 0 and delta_downloaded >= 0 and delta_epoch <= 10800:
                report_uploaded = info['report_uploaded']
                report_uploaded += delta_uploaded
                incomplete = info['incomplete']
                if incomplete >= 1:
                    report_uploaded += math.floor(delta_uploaded * random.uniform(*setting['uploaded']))
                    report_uploaded += math.floor(delta_downloaded * random.uniform(*setting['downloaded']))
                    percent = min(setting['percent_min'] + (incomplete - 1) * setting['percent_step'], setting['percent_max'])
                    if random.random() < percent:
                        report_uploaded += math.floor(delta_epoch * setting['speed'] * random.random())
                query['uploaded'] = report_uploaded
        self.con.execute('''REPLACE INTO
        torrent(info_hash, host, report_uploaded, uploaded, downloaded, epoch, incomplete)
        values (?, ?, ?, ?, ?, ?, ?)''',
                         (info_hash, host, report_uploaded, uploaded, downloaded, epoch, -2))
        self.con.commit()
        ctx.log.warn('%s up: %s/%s, down: %s, incomplete: %s, host: %s' %
                     (info_hash, format(report_uploaded), format(uploaded), format(downloaded), incomplete, host))

    def response(self, flow):
        pattern = re.compile('10:incompletei(\d+)e') # noqa
        content = flow.response.content.decode('ascii', 'ignore')
        match = pattern.search(content)
        if match:
            query = flow.request.query
            info_hash = query['info_hash'].encode('utf-8', 'surrogateescape').hex()
            incomplete = int(match.group(1))
            if int(query['left']) > 0 or ('event' in query and query['event'] == 'completed'):
                incomplete -= 1
            self.con.execute('''UPDATE torrent SET incomplete=? WHERE info_hash=?''',
                             (incomplete, info_hash))
            self.con.commit()
            ctx.log.warn('%s incomplete: %s' % (info_hash, incomplete))


addons = [
    TorrentRatio()
]
