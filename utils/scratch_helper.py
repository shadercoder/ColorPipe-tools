""" Scratch LUT helpers

.. moduleauthor:: `Marie FETIVEAU <github.com/mfe>`_

"""
__version__ = "0.1"
from utils.lut_utils import (check_arrays_length, int_scale_range,
                             LUTException)


def write_range(lutfile, values):
    """Write a range of values in a file

    Args:
        filename (str): out LUT path

        values (float array): values to write

    """
    for x in values:
        lutfile.write("      {0}\n".format(x))


def write_2d_scratch_lut(filename, xvalues, yvalues=None, zvalues=None):
    """Write an 1D or 2D Scratch LUT

    Args:
        filename (str): out LUT path

        xvalues (float array): 1st channel values

    Kwargs:
        yvalues (float array): 2nd channel values

        zvalues (float array): 3rd channel values

    """
    lutfile = open(filename, 'w+')
    lutfile.write("# Scratch LUT generated by ColorPipe-tools\n")
    sample_count = len(xvalues)
    max_value = sample_count - 1
    if yvalues is None or zvalues is None:
        # 1d LUT
        lutfile.write("LUT: 1 {0}\n".format(sample_count))
        xvalues = int_scale_range(xvalues, max_value)
        write_range(lutfile, xvalues)
    else:
        # 2d LUT
        try:
            check_arrays_length(xvalues, yvalues, zvalues)
        except LUTException, lut_exception:
            lutfile.close()
            raise lut_exception
        lutfile.write("LUT: 3 {0}\n".format(sample_count))
        xvalues = int_scale_range(xvalues, max_value)
        yvalues = int_scale_range(yvalues, max_value)
        zvalues = int_scale_range(zvalues, max_value)
        write_range(lutfile, xvalues)
        write_range(lutfile, yvalues)
        write_range(lutfile, zvalues)
    lutfile.close()


def write_1d_scratch_lut(filename, values):
    """ Write a 1D CSP LUT

    Args:
        filename (str): out LUT path

        values (float array): 1st channel values

    """
    write_2d_scratch_lut(filename, values)
