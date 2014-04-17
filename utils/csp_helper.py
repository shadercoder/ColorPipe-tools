""" CSP (Cinespace LUTs) helpers

.. moduleauthor:: `Marie FETIVEAU <github.com/mfe>`_

"""
__version__ = "0.2"
from utils.abstract_lut_helper import AbstractLUTHelper
from utils import lut_presets as presets
from utils.color_log_helper import (print_error_message,
                                    print_warning_message,
                                    print_success_message
                                    )


class CSPHelperException(Exception):
    """Module custom exception

    Args:
        Exception

    """
    pass


class CSPLutHelper(AbstractLUTHelper):
    """CST LUT helper

    """
    def __init__(self):
        self.default_preset = {
                presets.TYPE: "default",
                presets.EXT: ".csp",
                presets.IN_RANGE: [0.0, 1.0],
                presets.OUT_RANGE: [0.0, 1.0],
                presets.OUT_BITDEPTH: 12,
                presets.CUBE_SIZE: 17,
                presets.TITLE: "Csp LUT",
                presets.COMMENT: ("Generated by ColorPipe-tools, csp_helper "
                                 "{0}").format(__version__),
                presets.VERSION: "1"
                }

    def get_default_preset(self):
        return self.default_preset

    def __generic_write_lut(self, process_function, file_path, preset,
                            line_function, header_function, data_function):
        """ Write LUT
        CSP 1D / 3D are so similar that the same function cab be used  to
        write them

        Args:
            process_function (func): could be a processor.applyRGB
            (PyOpenColorIO.config.Processor) or a function that took a range
            of values and return the modified values. Ex: colorspace gradation
            functions

            preset (dict): lut generic and sampling informations

            line_function (function): describe how color values are written.
            Ex: "r g b" or "r, g, b" or "r".
            Use _get_rgb_value_line or _get_r_value_line

            header_function (func): get_1d_csp_header or get_3d_csp_header

            data_function (func): _get_1d_data and _get_3d_data

        """
        # Test output range
        self._check_range(preset)
        # Get data
        data = data_function(process_function, preset)
        lutfile = open(file_path, 'w+')
        lutfile.write(header_function(preset))
        # data
        for rgb in data:
            lutfile.write(line_function(preset, rgb))
        lutfile.close()
        print_success_message(self.get_export_message(file_path))

    def _write_1d_2d_lut(self, process_function, file_path, preset,
                         line_function):
        self.__generic_write_lut(process_function, file_path, preset,
                                 line_function,
                                 CSPLutHelper.get_1d_csp_header,
                                 self._get_1d_data)

    def write_1d_lut(self, process_function, file_path, preset):
        print_warning_message("1D LUT is not supported in Csp format"
                              " --> Switch to 2D LUT.")
        self.write_2d_lut(process_function, file_path, preset)

    def write_3d_lut(self, process_function, file_path, preset):
        self.__generic_write_lut(process_function, file_path, preset,
                                 self._get_rgb_value_line,
                                 CSPLutHelper.get_3d_csp_header,
                                 self._get_3d_data)

    @staticmethod
    def __get_csp_header(preset, mode, count_header):
        """Return CSP pre-LUT header

        Args:
            preset (dict): lut generic and sampling informations

            mode (str): 1D or 3D

            count_header (str): sample count for 1D/2D LUTs (ex: 1024) or axes
            segment count for 3D LUT (ex: "33 33 33")

        Returns:
            .str

        """
        input_range = preset[presets.IN_RANGE]
        output_range = preset[presets.OUT_RANGE]
        # TODO real shaper LUT management
        default_header = (
            "CSPLUTV100\n{4}\n\n"
            "2\n{0} {1}\n{2} {3}\n\n"
            "2\n{0} {1}\n{2} {3}\n\n"
            "2\n{0} {1}\n{2} {3}\n\n".format(input_range[0], input_range[1],
                                             output_range[0], output_range[1],
                                             mode)
        )
        return "{0}{1}\n".format(default_header, count_header)

    @staticmethod
    def get_1d_csp_header(preset):
        """Return CSP 1D pre-LUT header

        Args:
            preset (dict): lut generic and sampling informations

        Returns:
            .str

        """
        samples_count = pow(2,  preset[presets.OUT_BITDEPTH])
        return CSPLutHelper.__get_csp_header(preset, '1D', samples_count)

    @staticmethod
    def get_3d_csp_header(preset):
        """Return CSP 3D pre-LUT header

        Args:
            preset (dict): lut generic and sampling informations

        Returns:
            .str

        """
        header = "{0} {0} {0}".format(preset[presets.CUBE_SIZE])
        return CSPLutHelper.__get_csp_header(preset, '3D', header)

    @staticmethod
    def _get_range_message(range_name, arange):
        """ Get range warning/error message

        Returns:
            .str

        """
        return ("CSP {0} is expected to be float."
                " Ex: [0.0, 1.0] or [-0.25, 2.0].\nYour range {1}"
                ).format(range_name, arange)

    def _check_range(self, preset):
        """ Check output range. CSP LUT are float.
            Print a warning or raise an error

        """
        for str_range in ['input_range', 'output_range']:
            arange = preset[str_range]
            if self.is_int(arange):
                message = self._get_range_message(str_range, arange)
                print_error_message(message)
                raise CSPHelperException(message)
            elif arange[1] > presets.FLOAT_BOUNDARY:
                message = ("{0} seems too big !\n"
                       "Please check this, if the LUT isn't what you expected"
                       ).format(self._get_range_message(str_range, range))
                print_warning_message(message)

CSP_HELPER = CSPLutHelper()
