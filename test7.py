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
# core.set_max_cache_size(256)
num_frames = 1000
gpu = True
num_extra_iterations = 15

clipa = core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080, color=[112, 112, 220], length=num_frames)
clipb = core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080, color=[69, 45, 73], length=num_frames)
# clipc = core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080, color=[200, 119, 182], length=num_frames)


with Timer() as target:
    if gpu:
        clipa = core.std.TransferFrame(clipa, 1)
        clipb = core.std.TransferFrame(clipb, 1)
        # clipc = core.std.TransferFrame(clipc, 1)
        # "x 128 - abs y 128 - abs > x y ? 0.6 * x y + 0.2 * +"
        # "x 7 + y < x 2 + x 7 - y > x 2 - x 51 * y 49 * + 100 / ? ?"
    # clip = core.std.Expr(clips=[clipa, clipb, clipc], expr=["x y + z + 3 /", "", ""])
    # clip = core.std.Expr(clips=[clipa], expr=["x 128 - 1.49 * x 128 - dup * dup 9 + / * 128 +", "", ""])
    clip = core.std.Expr(clips=[clipa, clipb], expr=["x 7 + y < x 2 + x 7 - y > x 2 - x 51 * y 49 * + 100 / ? ?", "", ""])
    for i in range(num_extra_iterations):
        # clip = core.std.Expr(clips=[clipa, clipb, clip], expr=["x y + z + 3 /", "", ""])
        # clip = core.std.Expr(clips=[clip], expr=["x 128 - 1.49 * x 128 - dup * dup 9 + / * 128 +", "", ""])
        clip = core.std.Expr(clips=[clipa, clip], expr=["x 7 + y < x 2 + x 7 - y > x 2 - x 51 * y 49 * + 100 / ? ?", "", ""])

    if gpu:
        clip = core.std.TransferFrame(clip, 0)

    with open(os.devnull, 'w') as f:
        clip.output(f)

print("With extra_iterations = " + str(num_extra_iterations) + " gpu = " + str(gpu) + " threads = " + str(num_threads) + " elapsed time %f ms. Est. FPS = %f" % (target.elapsed, (num_frames / target.elapsed_secs)))

# clip.output(sys.stdout, y4m=True)
