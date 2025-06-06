'''
Stamp effect
'''
import typing
from PIL import Image
from .screenshot_effect import ScreenshotEffect


class StampEffect(ScreenshotEffect):
    '''
    Stamps another image onto the screenshot
    '''

    def __init__(self, glyph: Image.Image, position: typing.Tuple[int, int]):
        '''constructor'''
        super().__init__()
        self._glyph = glyph
        self._position = position

    def apply_to(self, screenshot: Image.Image) -> Image.Image:
        '''apply the effect'''

        cursor_pos = self._position
        cursor_img = self._glyph.copy()

        screenshot_width, screenshot_height = screenshot.size

        # scale the cursor stamp to a reasonable size
        cursor_size_ratio = min(max(screenshot_width / 2000, .3), max(screenshot_height / 2000, .3))

        # In some rare cases this could result in a decimal (0.xxxxx) which
        # causes a division by 0 error in PIL. Max creates a safe minimum.
        cursor_height = max(cursor_img.size[0] * cursor_size_ratio, 2)
        cursor_width = max(cursor_img.size[1] * cursor_size_ratio, 2)

        try:
            antialias_algo = Image.Resampling.LANCZOS
        except AttributeError: # PIL < 9.0
            antialias_algo = Image.ANTIALIAS # type: ignore

        cursor_img.thumbnail((int(cursor_width), int(cursor_height)), antialias_algo)

        # If the cursor glyph is square, center it
        if cursor_img.size[0] == cursor_img.size[1]:
            x_pos = cursor_pos[0] - round(.5*cursor_img.size[0])
            y_pos = cursor_pos[1] - round(.5*cursor_img.size[1])
            adjusted_pos = (
                x_pos if x_pos >= 0 else 0,
                y_pos if y_pos >= 0 else 0
            )
            cursor_pos = adjusted_pos

        # Passing cursor_img twice is intentional. The second time it's used
        # as a mask (PIL uses the alpha channel) so the cursor doesn't have
        # a black box.
        screenshot.paste(cursor_img, cursor_pos, cursor_img)
        return screenshot

    def __repr__(self):
        return f"StampEffect({self._glyph}, {self._position})"
