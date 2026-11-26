"""Branding regression tests: python -m unittest discover -s deliverables/budgetly -p 'test_*.py'."""
import unittest
from unittest.mock import patch
from PIL import Image, ImageChops
import render

class BrandingTests(unittest.TestCase):
    def assert_logo_at(self, image, xy, size):
        expected=render.background()
        logo=Image.open(render.R/'sources'/'budgetly-logo.png').convert('RGBA')
        logo.thumbnail((size,size),Image.Resampling.LANCZOS)
        x,y=xy
        expected.paste(logo,(x+(size-logo.width)//2,y+(size-logo.height)//2),logo)
        box=(x,y,x+size,y+size)
        self.assertIsNone(ImageChops.difference(image.crop(box),expected.crop(box)).getbbox())

    def test_asset_is_crop_of_original_not_redrawn(self):
        original=Image.open(render.R/'sources'/'budgetly-logo-original.png').convert('RGBA')
        x0,y0,x1,y1=original.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox()
        expected=original.crop((max(0,x0-2),max(0,y0-2),min(original.width,x1+2),min(original.height,y1+2)))
        self.assertEqual(render.LOGO.size,expected.size)
        self.assertEqual(render.LOGO.tobytes(),expected.tobytes())

    def test_logo_on_every_reel_and_cta(self):
        for slug,titles,phrases in render.DATA:
            for caption,shot,step in [phrases[0],('جرّب الديمو','dashboard','جرّب الديمو دابا')]:
                with self.subTest(slug=slug,shot=shot):
                    image=render.frame(titles,caption,shot,step,1)
                    self.assert_logo_at(image,(66,66),80)

    def test_logo_on_all_covers(self):
        for index,(slug,titles,_) in enumerate(render.DATA):
            with self.subTest(slug=slug),patch.object(Image.Image,'save',autospec=True) as save:
                render.cover(slug,titles,['dashboard','monthly','businesses'][index])
                self.assert_logo_at(save.call_args.args[0],(365,258),100)

if __name__=='__main__':unittest.main()
