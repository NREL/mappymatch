from __future__ import annotations

from typing import List

from mappymatch.constructs.trace import Trace


def split_large_trace(trace: Trace, ideal_size: int) -> List[Trace]:
    """
    split up a trace into a list of smaller traces

    :param trace:
    :param ideal_size:

    :return:
    """
    if len(trace) <= ideal_size:
        return [trace]
    else:
        ts = [trace[i : i + ideal_size] for i in range(0, len(trace), ideal_size)]

        # check to make sure the last trace isn't too small
        if len(ts[-1]) <= 10:
            last_trace = ts.pop()
            ts[-1] = ts[-1] + last_trace

        return ts


def remove_bad_start_from_trace(trace: Trace, distance_threshold: float) -> Trace:
    """
    remove points at the beginning of a trace if there is a gap larger than the distance threshold

    :param trace: the trace
    :param distance_threshold:

    :return: the new trace
    """

    def _trim_frame(frame):
        for index in range(len(frame)):
            rows = frame.iloc[index : index + 2]

            if len(rows) < 2:
                return frame

            current_point = rows.geometry.iloc[0]
            next_point = rows.geometry.iloc[1]

            if current_point != next_point:
                dist = current_point.distance(next_point)
                if dist > distance_threshold:
                    return frame.iloc[index + 1 :]
                else:
                    return frame

    return Trace.from_geo_dataframe(_trim_frame(trace._frame))
