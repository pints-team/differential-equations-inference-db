"""Function for loading hydrology data.
"""

import os
import pandas


def load_data(station_id):
    """Load river data from file.

    This function looks at data files which have been previously saved in the
    data directory.

    Parameters
    ----------
    station_id : str
        The USGS id for the weather station.
        03451500 = French Broad River at Asheville, North Carolina

    Returns
    -------
    pandas.DataFrame
        The data, with columns names year, month, day, precipitation,
        evaporation, streamflow, max_temp, and min_temp.
    """
    path = os.path.join(
        os.path.dirname(__file__), 'data', '{}.dly'.format(station_id))
    data_file = pandas.read_csv(path, sep='\t', header=None)

    # Add column names
    # See https://gist.github.com/josephguillaume/11199609
    data_file.columns = ['year',
                         'month',
                         'day',
                         'precipitation',
                         'evaporation',
                         'streamflow',
                         'max_temp',
                         'min_temp']

    return data_file
