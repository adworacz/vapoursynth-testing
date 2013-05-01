#!/usr/bin/env python3
import vapoursynth as vs
import sys
import os
from timeit import default_timer


class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.timer = default_timer

    def __enter__(self):
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        end = self.timer()
        self.elapsed_secs = end - self.start
        self.elapsed = self.elapsed_secs * 1000  # millisecs
        if self.verbose:
            print('elapsed time: %f ms' % self.elapsed)

num_threads = 1
core = vs.get_core(threads=num_threads)
core.set_max_cache_size(256)
gpu = False
num_frames = 1000
num_iterations = 16

core.std.LoadPlugin(path=r'/usr/local/lib/vapoursynth/libcuinvert.so')

ret = core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080, color=[69, 242, 115], length=num_frames)
# core.std.LoadPlugin(path=r'/usr/local/lib/libffms2.so')
# ret = core.ffms2.Source(source=r'sampleclip.mkv')

with Timer() as target:
    if gpu:
        ret = core.std.TransferFrame(ret, 1)
        for i in range(num_iterations):
            ret = core.cuinvert.Filter(ret)
        ret = core.std.TransferFrame(ret, 0)
    else:
        for i in range(num_iterations):
            ret = core.cuinvert.Filter(ret)

    with open(os.devnull, 'w') as f:
        ret.output(f)

print("With num_iterations = " + str(num_iterations) + ", gpu = " + str(gpu) + " and threads = " + str(num_threads) + ", elapsed time %f ms. Est. FPS = %f" % (target.elapsed, (ret.num_frames / target.elapsed_secs)))

# ret.output(sys.stdout, y4m=True)
