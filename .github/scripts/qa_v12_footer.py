#!/usr/bin/env python3
"""ABR-IT V12 media acceptance gate: catch Oct 13–14 opaque-logo regressions.

This conservative gate rejects the known pasted-black-square and fully black
footer regressions. It does not replace visual inspection of new artwork.
"""
import json
import sys

from PIL import Image


def fraction_black(image, bounds):
    sample = image.crop(bounds).convert('RGB')
    pixels = sample.getdata()
    count = sum(1 for (r, g, b) in pixels if max(r, g, b) <= 3)
    return count / (sample.width * sample.height)


def validate(path):
    with Image.open(path) as im:
        if im.format != 'PNG' or im.size != (1080, 1080):
            raise ValueError('EXPECTED_1080_SQUARE_PNG')
        im.load()
        # Bad RGB-pasted source logo x=806..1056,y=812..1062, black region ~90%;
        # original approved V12 graphics here ranged ~0..16%.
        tile = fraction_black(im, (812, 823, 1025, 897))
        strip = fraction_black(im, (32, 982, 1070, 1060))
        if tile > 0.75:
            raise ValueError('V12_FOOTER_OPAQUE_BLACK_LOGO_TILE')
        if strip > 0.75:
            raise ValueError('V12_FOOTER_OPAQUE_BLACK_STRIP')
        return {'passed':True,'size':[1080,1080],
                'logo_tile_black_fraction':round(tile,3),
                'footer_black_fraction':round(strip,3)}


if __name__ == '__main__':
    try:
        print(json.dumps(validate(sys.argv[1])))
    except (IndexError, OSError, ValueError) as exc:
        print('ABR-IT V12 MEDIA QA FAILED: '+str(exc), file=sys.stderr)
        sys.exit(1)
