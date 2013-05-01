#!/usr/bin/env python3
import vapoursynth as vs
import sys
import os

core = vs.get_core(threads=1)
gpu = True

core.std.LoadPlugin(path=r'/usr/local/lib/libffms2.so')
clip = core.ffms2.Source(source=r'sampleclip.mkv')
# # clip2 = core.std.Reverse(clip1)
# # mask = core.std.BlankClip(clip=clip1, color=[69, 242, 115])
# mask = core.std.BlankClip(clip=clip1, color=[255, 255, 255])

# clip2 = core.std.Turn180(clip1)

# if gpu:
#     clip = core.std.BlankClip(format=vs.YUV420P8, width=1280, height=528, color=[69, 242, 115], length=1000)
# else:
#     clip = core.std.BlankClip(format=vs.YUV420P8, width=1280, height=528, color=[69, 242, 115], length=1000)

if gpu:
    clip = core.std.TransferFrame(clip, 1)

# ret = core.std.Transpose(clip)
ret = core.std.Expr(clips=[clip], expr=["x 128 - 1.49 * x 128 - dup * dup 9 + / * 128 +", "", ""])

if gpu:
    ret = core.std.TransferFrame(ret, 0)

# with open(os.devnull, 'w') as f:
#     ret.output(f)

ret.output(sys.stdout)
