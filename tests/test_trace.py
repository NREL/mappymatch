from yamm.constructs.trace import Trace

trace = Trace.from_csv("../py-notebooks/Sample-2.csv")

trace = trace.downsample(1000)

print(len(trace))
