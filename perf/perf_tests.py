import vapoursynth as vs
from timer import Timer
import os
import csv
import inspect

class VSPerfTests(object):
    """Run a series of performance tests to collect metrics
    for Vapoursynth operations."""
    def __init__(self, writer, threads=1, frames=1000, iterations=1, gpu=False):
        self.threads = threads
        self.frames = frames
        self.gpu = gpu
        self.iterations = iterations
        self.core = vs.Core(threads=threads)
        self.writer = writer

    def __str__(self):
        return "Threads = %s Frames = %s GPU = %s Iterations = %s" % (self.threads, self.frames, self.gpu, self.iterations)

    def outputResults(self, filterName, target):
        # print("Elapsed time %f ms. Est. FPS = %f" % (target.elapsed, (self.frames / target.elapsed_secs)))
        self.writer.writerow([filterName, target.elapsed, (self.frames / target.elapsed_secs)])

    def measureExpr(self):
        """ Expr """
        clipa = self.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080, color=[112, 112, 220], length=self.frames)
        clipb = self.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080, color=[69, 45, 73], length=self.frames)
        # clipc = core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080, color=[200, 119, 182], length=num_frames)

        with Timer() as target:
            if self.gpu:
                clipa = self.core.std.TransferFrame(clipa, 1)
                clipb = self.core.std.TransferFrame(clipb, 1)
                # clipc = core.std.TransferFrame(clipc, 1)
                # "x 128 - abs y 128 - abs > x y ? 0.6 * x y + 0.2 * +"

            # clip = core.std.Expr(clips=[clipa, clipb, clipc], expr=["x y + z + 3 /", "", ""])
            # clip = core.std.Expr(clips=[clipa], expr=["x 128 - 1.49 * x 128 - dup * dup 9 + / * 128 +", "", ""])
            clip = self.core.std.Expr(clips=[clipa, clipb], expr=["x 7 + y < x 2 + x 7 - y > x 2 - x 51 * y 49 * + 100 / ? ?", "", ""])
            for i in range(self.iterations - 1):
                # clip = core.std.Expr(clips=[clipa, clipb, clip], expr=["x y + z + 3 /", "", ""])
                # clip = core.std.Expr(clips=[clip], expr=["x 128 - 1.49 * x 128 - dup * dup 9 + / * 128 +", "", ""])
                clip = self.core.std.Expr(clips=[clipa, clip], expr=["x 7 + y < x 2 + x 7 - y > x 2 - x 51 * y 49 * + 100 / ? ?", "", ""])

            if self.gpu:
                clip = self.core.std.TransferFrame(clip, 0)

            with open(os.devnull, 'w') as f:
                clip.output(f)

        self.outputResults("Expr", target)

    def measureTranspose(self):
        """ Transpose """
        clip = self.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080, color=[112, 112, 220], length=self.frames)

        with Timer() as target:
            if self.gpu:
                clip = self.core.std.TransferFrame(clip, 1)

            clip = self.core.std.Transpose(clip)

            if self.gpu:
                clip = self.core.std.TransferFrame(clip, 0)

            with open(os.devnull, 'w') as f:
                clip.output(f)

        self.outputResults("Transpose", target)

    def measureLUT(self):
        """ LUT """
        clip = self.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080, color=[112, 112, 220], length=self.frames)

        luty = []
        for x in range(2**clip.format.bits_per_sample):
           luty.append(max(min(x, 235), 16))

        with Timer() as target:
            if self.gpu:
                clip = self.core.std.TransferFrame(clip, 1)

            clip = self.core.std.Lut(clip=clip, lut=luty, planes=0)

            if self.gpu:
                clip = self.core.std.TransferFrame(clip, 0)

            with open(os.devnull, 'w') as f:
                clip.output(f)

        self.outputResults("LUT", target)

    def measureMerge(self):
        """ Merge """
        clipa = self.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080, color=[112, 112, 220], length=self.frames)
        clipb = self.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080, color=[69, 45, 73], length=self.frames)

        with Timer() as target:
            if self.gpu:
                clip = self.core.std.TransferFrame(clip, 1)

            clip = self.core.std.Merge(clips=[clipa,clipb])

            if self.gpu:
                clip = self.core.std.TransferFrame(clip, 0)

            with open(os.devnull, 'w') as f:
                clip.output(f)

        self.outputResults("Merge", target)

def performTests(pt, writer):
    def pred(object):
        return inspect.ismethod(object) and object.__name__.startswith("measure")

    tests = inspect.getmembers(pt, pred)

    writer.writerow([str(pt)])
    writer.writerow(["", "Elapsed Time", "Est. FPS"])

    print(pt)
    for test, method in tests:
        print("Running: " + method.__doc__)
        method()

if __name__ == '__main__':
    csvfile = open('results.csv', 'w', newline='')
    writer = csv.writer(csvfile)

    for threads in [1, 2, 4, 8]:
        for iterations in [1]:
            # for gpu in range(2):
            performTests(VSPerfTests(writer=writer, threads=threads, frames=1000, iterations=iterations, gpu=False), writer)

    csvfile.close()