from unittest import TestCase

from yamm.constructs.coordinate import Coordinate
from yamm.constructs.trace import Trace
from yamm.utils.geo import compute_bounding_box


class TestBoundingBox(TestCase):

    def test_compute_bounding_box(self):
        # the proper bounding box for this is a box with corners at 0,0 and 2,2
        mock_coords = [
            Coordinate.from_xy(0, 0),
            Coordinate.from_xy(1, 1),
            Coordinate.from_xy(2, 2),
        ]

        mock_trace = Trace(mock_coords)

        bbox = compute_bounding_box(mock_trace)

        self.assertEquals(bbox.southwest_corner, mock_coords[0])
        self.assertEquals(bbox.northeast_corner, mock_coords[-1])

    def test_compute_bounding_box_w_padding(self):
        # the proper bounding box for this with padding of 5 is a box with corners at -5,-5 and 7,5
        mock_coords = [
            Coordinate.from_xy(0, 0),
            Coordinate.from_xy(1, 0),
            Coordinate.from_xy(2, 0),
        ]

        mock_trace = Trace(mock_coords)

        bbox = compute_bounding_box(mock_trace, padding=5)

        self.assertEquals(bbox.southwest_corner.x, -5)
        self.assertEquals(bbox.southwest_corner.y, -5)
        self.assertEquals(bbox.northeast_corner.x, 7)
        self.assertEquals(bbox.northeast_corner.y, 5)
