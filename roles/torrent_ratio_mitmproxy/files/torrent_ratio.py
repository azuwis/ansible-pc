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
            'speed': 51200,
            'port': 0,
            'peer_id': ''
        }
        high = { # noqa
            'uploaded': (2, 4),
            'downloaded': (0.08, 0.1),
            'percent_min': 0.4,
            'percent_max': 0.7,
            'percent_step': 0.06,
            'speed': 102400,
            'port': 0,
            'peer_id': ''
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
        req_info = {}
        req_info['info_hash'] = query['info_hash'].encode('utf-8', 'surrogateescape').hex()
        req_info['uploaded'] = int(query['uploaded'])
        req_info['downloaded'] = int(query['downloaded'])
        req_info['host'] = flow.request.pretty_host
        setting = self.setting['default']
        if req_info['host'] in self.setting:
            setting = self.setting[req_info['host']]
        if setting['peer_id'] != '':
            query['peer_id'] = '-{}-'.format(setting['peer_id'])
        if setting['port'] > 0 and setting['port'] < 65536:
            query['port'] = setting['port']
        req_info['epoch'] = time.time()
        req_info['report_uploaded'] = req_info['uploaded']
        req_info['incomplete'] = -2
        init = ''
        prev_req_info = self.con.execute('''SELECT * FROM torrent WHERE info_hash=?''', (info_hash,)).fetchone()
        if not prev_req_info:
            init = 'init, '
        else:
            if ('event' not in query or query['event'] != 'started'):
                delta_uploaded = req_info['uploaded'] - prev_req_info['uploaded']
                delta_downloaded = req_info['downloaded'] - prev_req_info['downloaded']
                delta_epoch = req_info['epoch'] - prev_req_info['epoch']
                if delta_uploaded >= 0 and delta_downloaded >= 0 and delta_epoch <= 10800:
                    req_info['report_uploaded'] = prev_req_info['report_uploaded']
                    req_info['report_uploaded'] += delta_uploaded
                    if prev_req_info['incomplete'] >= 1:
                        req_info['report_uploaded'] += math.floor(delta_uploaded * random.uniform(*setting['uploaded']))
                        req_info['report_uploaded'] += math.floor(delta_downloaded * random.uniform(*setting['downloaded']))
                        percent = min(setting['percent_min'] + (prev_req_info['incomplete'] - 1) * setting['percent_step'], setting['percent_max'])
                        if random.random() < percent:
                            req_info['report_uploaded'] += math.floor(delta_epoch * setting['speed'] * random.random())
                    query['uploaded'] = req_info['report_uploaded']
        self.con.execute('''REPLACE INTO
        torrent(info_hash, host, report_uploaded, uploaded, downloaded, epoch, incomplete)
        values (?, ?, ?, ?, ?, ?, ?)''',
                         (req_info['info_hash'], req_info['host'], req_info['report_uploaded'], req_info['uploaded'],
                          req_info['downloaded'], req_info['epoch'], req_info['incomplete']))
        self.con.commit()
        ctx.log.warn('%s %sup: %s/%s, down: %s, host: %s, epoch: %s' %
                     (req_info['info_hash'], init, format(req_info['report_uploaded']), format(req_info['uploaded']),
                      format(req_info['downloaded']), req_info['host'], req_info['epoch']))

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
            ctx.log.warn('%s incomplete: %d' % (info_hash, incomplete))


addons = [
    TorrentRatio()
]
