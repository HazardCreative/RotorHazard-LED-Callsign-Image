'''LED visual effects'''

# displays "static/user/[callsign].png" on an LED panel when activated
# shows assigned color if none exists
# to use this handler, run:
#    sudo apt-get install libjpeg-dev
#    sudo pip install pillow
#    sudo apt-get install libopenjp2-7-dev

import Config
from eventmanager import Evt
from led_event_manager import LEDEffect, LEDEvent, Color
import gevent
import os
from PIL import Image, ImageDraw

def leaderProxy(args):
    try:
        result = args['RHAPI'].race.results
        leaderboard = result[result['meta']['primary_leaderboard']]
        leader = leaderboard[0]
        if leader['starts']:
            if 'node_index' not in args or args['node_index'] != leader['node']:
                args['pilot_id'] = leader['pilot_id']
                args['color'] = args['manager'].getDisplayColor(leader['node'], from_result=True)
            args['effect_fn'](args)
            return True
    except:
        return False

def userBitmap(args):
    try:
        callsign = args['RHAPI'].db.pilot_by_id(args['pilot_id']).callsign

        args['bitmaps'] = [
            {"image": "static/user/" + callsign + ".png", "delay": 0}
        ]
        showBitmap(args)
    except:
        return False

def showBitmap(args):
    if 'strip' in args:
        strip = args['strip']
    else:
        return False

    def setPixels(img):
        pos = 0
        for row in range(0, img.height):
            for col in range(0, img.width):
                if pos >= strip.numPixels():
                    return

                c = col
                if Config.LED['INVERTED_PANEL_ROWS']:
                    if row % 2 == 0:
                        c = 15 - col

                px = img.getpixel((c, row))
                strip.setPixelColor(pos, Color(px[0], px[1], px[2]))
                pos += 1

    bitmaps = args['bitmaps']
    if bitmaps and bitmaps is not None:
        for bitmap in bitmaps:
            if os.path.exists(bitmap['image']):
                img = Image.open(bitmap['image'])
            else:
                img = Image.new('RGB', (1, 1))
                draw = ImageDraw.Draw(img)
                if 'color' in args:
                    draw.rectangle((0, 0, 1, 1), fill=convertColor(args['color']))
                else:
                    draw.rectangle((0, 0, 1, 1), fill=(127, 127, 127))

            panel_w = Config.LED['LED_COUNT'] // Config.LED['LED_ROWS']
            panel_h = Config.LED['LED_ROWS']

            if Config.LED['PANEL_ROTATE'] % 2:
                output_w = panel_h
                output_h = panel_w
            else:
                output_w = panel_w
                output_h = panel_h

            size = img.size

            ratio_w = output_w / size[0]
            ratio_h = output_h / size[1]

            ratio = min(ratio_w, ratio_h)

            img = img.resize((int(size[0]*ratio), int(size[1]*ratio)))

            output_img = Image.new(img.mode, (output_w, output_h))
            size = img.size
            pad_left = int((output_w - size[0]) / 2) 
            pad_top = int((output_h - size[1]) / 2)
            output_img.paste(img, (pad_left, pad_top))
            output_img = output_img.rotate(90 * Config.LED['PANEL_ROTATE'], expand=True)

            setPixels(output_img)
            strip.show()
            delay = bitmap['delay']
            gevent.sleep(delay/1000.0)

def convertColor(color):
    return color >> 16, (color >> 8) % 256, color % 256

def register_handlers(args):
    for led_effect in [
        LEDEffect("Image: user/[callsign].png", userBitmap, {
                'manual': False,
                'include': [Evt.CROSSING_ENTER, Evt.CROSSING_EXIT, Evt.RACE_LAP_RECORDED, Evt.RACE_WIN],
                'exclude': [Evt.ALL],
                'recommended': [Evt.CROSSING_ENTER, Evt.CROSSING_EXIT, Evt.RACE_LAP_RECORDED, Evt.RACE_WIN],
            }, {
                'time': 5
            },
            name = "bitmapCallsign",
        ),
        LEDEffect("Image: user/[callsign].png / Leader", leaderProxy, {
                'include': [Evt.RACE_LAP_RECORDED, LEDEvent.IDLE_RACING, LEDEvent.IDLE_DONE, Evt.RACE_WIN],
                'exclude': [Evt.ALL],
                'recommended': [Evt.RACE_LAP_RECORDED, Evt.RACE_WIN]
            }, {
                'effect_fn': userBitmap,
                'time': 5
            },
            name="bitmapCallsignLeader",
        ),
    ]:
        args['register_fn'](led_effect)

def initialize(rhapi):
    rhapi.events.on(Evt.LED_INITIALIZE, register_handlers)

