import logging
import subprocess
import typing
from gscreenshot.scaling import get_scaling_factor, get_scaling_method_name
from gscreenshot.util import GSCapabilities
from .exceptions import SelectionError, SelectionExecError, SelectionCancelled, SelectionParseError


log = logging.getLogger(__name__)

class RegionSelector():
    '''Region selection interface'''

    __utilityname__: str = "default"

    def __init__(self):
        """
        constructor
        """

    def get_capabilities(self) -> typing.Dict[str, str]:
        """
        Get supported features. Note that under-the-hood the capabilities
        of the selector (if applicable) will be added to this.

        Returns:
            [GSCapabilities]
        """
        return {}

    def get_capabilities_(self) -> typing.Dict[str, str]:
        """
        Get the features this selector supports
        """
        capabilities = self.get_capabilities()

        capabilities.update({
            GSCapabilities.WINDOW_SELECTION: self.__utilityname__,
            GSCapabilities.REGION_SELECTION: self.__utilityname__,
            GSCapabilities.REUSE_REGION: self.__utilityname__
        })

        if GSCapabilities.SCALING_DETECTION not in capabilities:
            scaling_name = get_scaling_method_name()
            capabilities[GSCapabilities.SCALING_DETECTION] = scaling_name

        return capabilities

    def region_select(self,
                      selection_box_rgba: typing.Optional[str] = None,
                      selection_border_weight: typing.Optional[int] = None,
                      ) -> typing.Tuple[int, int, int, int]:
        """
        Select an arbitrary region of the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        raise SelectionError("Not implemented")

    def window_select(self,
                      selection_box_rgba: typing.Optional[str]=None,
                      selection_border_weight: typing.Optional[int]=None,
                      ) -> typing.Tuple[int, int, int, int]:
        """
        Selects a window from the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        raise SelectionError("Not implemented")

    @staticmethod
    def can_run() -> bool:
        """
        Returns whether this is capable of running.
        """
        return False

    def _get_boundary_interactive(self, params: typing.List[str]
                                ) -> typing.Optional[typing.Tuple[float, float, float, float]]:
        """
        Runs the selector and returns the parsed output. This accepts a list
        that will be passed directly to subprocess.Popen and expects the
        utility to be capable of returning a string parseable by _parse_selection_output.
        """
        try:
            with subprocess.Popen(
                    params,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
            ) as selector_process:

                try:
                    log.debug("running selector %s", params)
                    stdout, stderr = selector_process.communicate(timeout=60)
                except subprocess.TimeoutExpired:
                    selector_process.kill()
                    #pylint: disable=raise-missing-from
                    log.warning("selection timed out")
                    raise SelectionExecError(f"{params[0]} selection timed out")

                return_code = selector_process.returncode

                if return_code != 0:
                    selector_error = stderr.decode("UTF-8")

                    if "cancelled" in selector_error:
                        raise SelectionCancelled("Selection was cancelled")

                    raise SelectionExecError(selector_error)

                selector_output = stdout.decode("UTF-8").strip().split("\n")

                return self._parse_selection_output(selector_output)
        except OSError:
            #pylint: disable=raise-missing-from
            raise SelectionExecError(f"{params[0]} was not found") #from exception
        except subprocess.CalledProcessError as exc:
            log.info("failed to run %s: %s", params, exc)

        return None

    def _parse_selection_output(self, region_output: typing.List[str]
                                ) -> typing.Tuple[float, float, float, float]:
        '''
        Parses output from a region selection tool in the format
        X=%x,Y=%y,W=%w,H=%h OR X=%x\nY=%x\nW=%w\nH=%h.

        Returns a tuple of the X and Y coordinates of the corners:
        (X top left, Y top left, X bottom right, Y bottom right)
        '''
        log.debug("parsing selector output '%s'", region_output)
        region_parsed = {}
        # We iterate through the output so we're not reliant
        # on the order or number of lines in the output
        for line in region_output:
            for comma_split in line.split(","):
                if '=' in comma_split:
                    spl = comma_split.split("=")
                    region_parsed[spl[0]] = int(spl[1])

        if GSCapabilities.SCALING_DETECTION in self.get_capabilities():
            log.debug(
                "region backend is already handling scale factor - skipping adjustment",
            )
            scaling_factor = 1.0
        else:
            scaling_factor = get_scaling_factor()

        # (left, upper, right, lower)
        try:
            crop_box = (
                region_parsed['X'] * scaling_factor,
                region_parsed['Y'] * scaling_factor,
                (region_parsed['X'] + region_parsed['W']) * scaling_factor,
                (region_parsed['Y'] + region_parsed['H']) * scaling_factor,
            )
        except KeyError:
            #pylint: disable=raise-missing-from
            log.info("unparseable region")
            raise SelectionParseError("Unexpected output") #from exception

        log.debug("got crop box %s", crop_box)
        return crop_box

    @staticmethod
    def _rgba_hex_to_decimals(selection_box_rgba: typing.Optional[str]
                          ) -> typing.Tuple:
        log.debug("converting '%s' to RGB(A) decimals", selection_box_rgba)
        selection_box_rgba = selection_box_rgba if selection_box_rgba else "#cccccc99"
        selection_box_rgba = selection_box_rgba.strip("#").strip()
        color = None

        try:
            color = tuple(float(int(selection_box_rgba[i:i+2], 16)/255) for i in (0, 2, 4, 6))
        except (IndexError, ValueError):
            log.debug(
                "RGB(A) input '%s' is missing alpha channel - retrying without alpha",
                selection_box_rgba
            )

        if not color:
            try:
                color = tuple(float(int(selection_box_rgba[i:i+2], 16)/255) for i in (0, 2, 4))
            except (IndexError, ValueError) as exc:
                log.info(
                    "RGB(A) input '%s' is invalid, using defaults: %s",
                    selection_box_rgba,
                    exc
                )
                color = (0.8, 0.8, 0.8, 0.6)

        return color

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}()'
