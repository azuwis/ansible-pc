from mitmproxy import ctx
import json
import math
import os
import random
import re
import time


class TorrentRatio:
    def __init__(self):
        low = {
            'uploaded': (.1, .6),
            'downloaded': (0, .07),
            'percent_multi': .2,
            'percent_max': .5,
            'speed': 102400
        }
        high = {
            'uploaded': (2, 4),
            'downloaded': (.08, .1),
            'percent_multi': .4,
            'percent_max': .7,
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
        self.dump_file = os.path.join(os.path.dirname(__file__), 'torrent_ratio.json')
        self.torrent = {}
        if os.path.isfile(self.dump_file):
            with open(self.dump_file, 'r') as dump_file:
                self.torrent = json.load(dump_file)

    def done(self):
        with open(self.dump_file, 'w') as dump_file:
            json.dump(self.torrent, dump_file)

    def request(self, flow):
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
        if ('event' not in query or query['event'] != 'started') and info_hash in self.torrent:
            info = self.torrent[info_hash]
            delta_uploaded = uploaded - info['uploaded']
            delta_downloaded = downloaded - info['downloaded']
            delta_epoch = epoch - info['epoch']
            if delta_uploaded >= 0 and delta_downloaded >= 0 and delta_epoch <= 10800:
                report_uploaded = info['report_uploaded']
                report_uploaded += delta_uploaded
                incomplete = info['incomplete'] if 'incomplete' in info else 0
                if incomplete > 0:
                    report_uploaded += math.floor(delta_uploaded * random.uniform(*setting['uploaded']))
                    report_uploaded += math.floor(delta_downloaded * random.uniform(*setting['downloaded']))
                    percent = min(incomplete * setting['percent_multi'], setting['percent_max'])
                    if random.random() < percent:
                        report_uploaded += math.floor(delta_epoch * setting['speed'] * random.random())
                query['uploaded'] = report_uploaded
        self.torrent[info_hash] = {
            'host': host,
            'report_uploaded': report_uploaded,
            'uploaded': uploaded,
            'downloaded': downloaded,
            'epoch': epoch
        }
        ctx.log.warn('%s: %s' % (info_hash, json.dumps(self.torrent[info_hash])))

    def response(self, flow):
        pattern = re.compile('10:incompletei(\d+)e')
        content = flow.response.content.decode('ascii', 'ignore')
        match = pattern.search(content)
        if match:
            query = flow.request.query
            info_hash = query['info_hash'].encode('utf-8', 'surrogateescape').hex()
            incomplete = int(match.group(1))
            self.torrent[info_hash]['incomplete'] = incomplete

addons = [
    TorrentRatio()
]
