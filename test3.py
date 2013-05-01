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
num_frames = 1000
gpu = True
num_extra_iterations = 0

clip = core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080, color=[69, 242, 115], length=num_frames)

luty = []
for x in range(2 ** clip.format.bits_per_sample):
    luty.append(max(min(x, 235), 16))
lutuv = []
for x in range(2 ** clip.format.bits_per_sample):
    lutuv.append(max(min(x, 100), 16))

with Timer() as target:
    if gpu:
        clip = core.std.TransferFrame(clip, 1)

    ret = core.std.Lut(clip=clip, lut=luty, planes=0)
    ret = core.std.Lut(clip=ret, lut=lutuv, planes=[1, 2])
    for i in range(num_extra_iterations):
        ret = core.std.Lut(clip=ret, lut=luty, planes=0)
        ret = core.std.Lut(clip=ret, lut=lutuv, planes=[1, 2])

    if gpu:
        ret = core.std.TransferFrame(ret, 0)

    with open(os.devnull, 'w') as f:
        ret.output(f)

print("With extra_iterations = " + str(num_extra_iterations) + " gpu = " + str(gpu) + " threads = " + str(num_threads) + " elapsed time %f ms. Est. FPS = %f" % (target.elapsed, (num_frames / target.elapsed_secs)))

# ret.output(sys.stdout, y4m=True)
