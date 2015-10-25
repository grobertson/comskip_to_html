#!/home/chinachu/chinachu-scripts/comskip_to_x/env3/bin/python
# coding: utf-8

import base64
import datetime
from io import BytesIO
import os.path
import sys

import click
import ffms
from PIL import Image
import jinja2


def to_timestamp(seconds):
    td = datetime.timedelta(seconds=seconds)
    return str(td)[:-3]


class FFMSVideo:
    def __init__(self, videofile):
        self.vs = ffms.VideoSource(videofile, num_threads=1)
        self.keyframes = self.vs.track.keyframes

    def set_scale(self, scale):
        f = self.vs.get_frame(0)
        h = int(f.EncodedHeight * scale)
        w = int(f.EncodedWidth * scale)
        self.vs.set_output_format(width=w, height=h)

    def _get_img_by_frame(self, frame):
        h = frame.ScaledHeight
        w = frame.ScaledWidth

        return Image.fromarray(frame.planes[0].reshape(h, w)).crop(box=(0, 0, frame.ScaledWidth, frame.ScaledHeight))

    def get_frame_img(self, number, dataurl=False):
        if number < 0:
            number = 0
        if number >= self.vs.properties.NumFrames:
            number = self.vs.properties.NumFrames - 1
        try:
            frame = self.vs.get_frame(number)
        except ffms.Error as e:
            click.echo("number: %d" % number, err=True)
            click.echo(str(e), err=True)
            raise e
        img = self._get_img_by_frame(frame)
        if dataurl:
            f = BytesIO()
            img.save(f, "JPEG")
            return 'data:img/jpeg;base64,' + base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        return img

    def get_near_keyframes(self, frame, delta=60):
        return [x for x in self.keyframes if frame - delta <= x <= frame + delta]

    def get_pts(self, frame):
        info = self.vs.track.frame_info_list[frame]
        return (info.PTS - self.vs.track.frame_info_list[0].PTS) * self.vs.track.time_base.Num / (self.vs.track.time_base.Den * 1000)


class ComSkipResult:
    def __init__(self, videofile):
        if not os.path.exists(videofile):
            raise "videofile: %s not found" % videofile
        self.video = FFMSVideo(videofile)
        self.videofile = videofile
        (basename, ext) = os.path.splitext(videofile)
        self.basename = basename
        log = "%s.log" % basename
        if os.path.exists(log):
            with open(log) as f:
                for line in f:
                    if line.startswith("Block list after weighing"):
                        break
                f.readline()
                f.readline()
                self.blocks = []
                for line in f:
                    if line == "\n":
                        break
                    block = {}
                    block["no"] = int(line[0:3])
                    block["isCM"] = (line[4:6] == "--")
                    block["sbf"] = int(line[6:11])
                    block["bs"] = int(line[11:15])
                    block["be"] = int(line[15:19])
                    block["fs"] = int(line[19:26])
                    block["fe"] = int(line[26:33])
                    block["ts"] = float(line[33:42])
                    block["te"] = float(line[43:52])
                    block["len"] = float(line[53:62])
                    block["sc"] = float(line[63:70])
                    block["scr"] = float(line[70:76])
                    block["cmb"] = int(line[76:80])
                    block["ar"] = float(line[80:85])
                    cut = line[96:106]
                    block["bri"] = int(line[107:113])
                    block["bricode"] = line[113]
                    block["logo"] = float(line[115:119])
                    block["vol"] = int(line[120:124])
                    block["volcode"] = line[124]
                    block["sil"] = int(line[125:128])
                    block["silcode"] = line[128]
                    block["corr"] = float(line[130:136])
                    block["stdev"] = int(line[137:142])
                    block["cc"] = line[143:]
                    block["line"] = line

                    cutreason = []
                    r = {"F": "F:scene", "A": "A:aspect", "E": "E:exceeds", "L": "L:logo", "B": "B:bright",
                         "C": "C:combined", "N": "N:nonstrict", "S": "S:strict", "c": "c:change", "t": "t:cutscene",
                         "l": "l:logo", "v": "v:volume", "s": "s:scene_change", "a": "a:aspect_ratio",
                         "u": "u:uniform_frame", "b": "b:black_frame", "r": "r:resolution"}
                    for c in cut:
                        if c in r:
                            cutreason.append(r[c])

                    block["cut"] = ", ".join(cutreason)

                    self.blocks.append(block)

    def to_html(self):
        self.video.set_scale(1 / 12)
        f = self.video.vs.get_frame(0)
        w = f.ScaledWidth
        h = f.ScaledHeight
        tmpl_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(sys.argv[0])), autoescape=False)
        tmpl = tmpl_env.get_template("comskip_to_html.tmpl")
        tmpl_vars = {"videofile": self.videofile, "comskip": self, "to_timestamp": to_timestamp, "w": w, "h": h}
        with open(self.basename + ".html", "w", encoding="utf-8") as f:
            f.write(tmpl.render(tmpl_vars))


@click.command()
@click.argument('videofile', type=click.Path(exists=True))
def to_html(videofile):
    comskip = ComSkipResult(videofile)
    comskip.to_html()


if __name__ == '__main__':
    to_html()
