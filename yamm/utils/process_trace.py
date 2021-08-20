from __future__ import annotations

from yamm.constructs.trace import Trace


def remove_bad_start_from_trace(trace: Trace, distance_threshold: float):
    """
    remove points at the beginning of a trace if there is a gap larger than the distance threshold

    :param trace: the trace
    :param distance_threshold:

    :return: the new trace
    """
    def _trim_frame(frame):
        for index in frame.index:
            rows = frame.loc[index:index + 1]

            if len(rows) < 2:
                return frame

            current_point = rows.geometry.iloc[0]
            next_point = rows.geometry.iloc[1]

            if current_point != next_point:
                dist = current_point.distance(next_point)
                if dist > distance_threshold:
                    return frame.loc[index + 1:]
                else:
                    return frame

    return Trace.from_geo_dataframe(_trim_frame(trace._frame))
