import geopy
import geopy.distance

def calculate_geodistance(point_one,link_point):

    """
    calculates distance between point_one and link_point.

    Args:
        point_one (_type_): _description_
        link_point (_type_): _description_

    Returns:
        _type_: _description_
    """


    coords_1 = (point_one[0], point_one[1])
    coords_2 = (link_point[0], link_point[1])

    total_distance = geopy.distance.geodesic(coords_1, coords_2).m

    return total_distance


x = calculate_geodistance([52.2296756, 21.0122287],[52.406374, 16.9251681])

print(x)