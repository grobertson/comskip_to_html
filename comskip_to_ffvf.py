#!/home/chinachu/chinachu-scripts/comskip_to_x/env3/bin/python
# coding: utf-8

import click
import datetime


def to_timestamp(s):
    return str(datetime.timedelta(seconds=s))[:-3].replace(':', r'\:')


@click.command()
@click.argument('logfile', type=click.File("r", encoding="utf-8"))
def to_ffvf(logfile):
    for line in logfile:
        if line.startswith("Block list after weighing"):
            break
    logfile.readline()
    logfile.readline()

    blocks = []
    for line in logfile:
        if line == '\n':
            break
        block = {}
        block["no"] = int(line[0:3])
        block["isCM"] = (line[4:6] == "--")
        block["fs"] = int(line[19:26])
        block["fe"] = int(line[26:33])
        block["ts"] = float(line[33:42])
        block["te"] = float(line[43:52])
        block["len"] = float(line[53:62])
        blocks.append(block)

    vfs = []
    for b in blocks:
        start = to_timestamp(b["ts"])
        end = to_timestamp(b["te"])
        if b["isCM"]:
            # vf = "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:x=5:y=5:text='#%02d[CM]START\:%s END\:%s':fontsize=36:fontcolor=white@0.9:box=1:boxcolor=magenta@0.5:borderw=4:boxborderw=4:bordercolor=red@1.0:enable='gte(t,%f)*lt(t,%f)'" % (b["no"], start, end, b['ts'], b['te'])
            vf = "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:x=5:y=5:text='#%02d[CM]START\:%s END\:%s':fontsize=40:fontcolor=magenta@0.4:box=1:boxcolor=white@0.2:borderw=2:bordercolor=red@0.6:enable='gte(n,%f)*lte(n,%f)'" % (b["no"], start, end, b['fs'], b['fe'])
        else:
            # vf = "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:x=5:y=5:text='#%02d[--]START\:%s END\:%s':fontsize=36:fontcolor=white@0.9:box=1:boxcolor=limegreen@0.5:borderw=4:boxborderw=4:bordercolor=green@1.0:enable='gte(t,%f)*lt(t,%f)'" % (b["no"], start, end, b["ts"], b["te"])
            vf = "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:x=5:y=5:text='#%02d[MV]START\:%s END\:%s':fontsize=40:fontcolor=limegreen@0.4:box=1:boxcolor=white@0.2:borderw=2:bordercolor=green@0.6:enable='gte(n,%f)*lte(n,%f)'" % (b["no"], start, end, b["fs"], b["fe"])
        vfs.append(vf)
    click.echo(",".join(vfs))

if __name__ == '__main__':
    to_ffvf()
