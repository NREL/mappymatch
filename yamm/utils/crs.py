from pyproj import CRS

LATLON_CRS = CRS(4326)
XY_CRS = CRS(3857)

def change_crs(current_mode):
    """
    change from latlon to xy_crs or the other way.

    Args:
        current_mode (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    if str(current_mode) == "LATLON_CRS":
        current_mode = XY_CRS
    elif str(current_mode) == "XY_CRS":
        current_mode = LATLON_CRS
    else:
        raise ValueError("CRS is not LatLon_CRS or XY_CRS")
    
    return current_mode