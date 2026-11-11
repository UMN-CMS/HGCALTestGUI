"""Snapshot processing, and the decoder running in a separate process.

The decoder (dm_rebuild) is pure-Python number crunching. In a thread it holds
Python's GIL for seconds at a time and the video loop stutters, so it lives in its
own process.
"""
import multiprocessing as mp
import os
import queue

import cv2 as cv

import dm_rebuild

# Sliders process() reads
PIPELINE_SLIDERS = ('Blur', 'Threshold mode', 'Manual Threshold', 'Adaptive size',
                    'Adaptive offset')


def square(k):
    # Square kernel keeps square cells square (round kernels shave the corners off)
    return cv.getStructuringElement(cv.MORPH_RECT, (k, k))


def process(smooth, p, clahe):
    """Averaged grayscale frame -> processed image (dark code on white).

    p maps slider name -> value. Returns (image, threshold Otsu picked or None).
    """
    # Spatial smoothing + contrast
    b = p['Blur']
    if b:
        smooth = cv.GaussianBlur(smooth, (2 * b + 1, 2 * b + 1), 0)

    # Threshold (white = brighter than cutoff)
    mode = p['Threshold mode']
    otsu_t = None
    if mode == 1:
        otsu_t, binary = cv.threshold(smooth, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    elif mode == 2:
        block = p['Adaptive size'] | 1  # must be odd
        off = p['Adaptive offset']
        binary = cv.adaptiveThreshold(smooth, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv.THRESH_BINARY, block, -off)
    else:
        _, binary = cv.threshold(smooth, p['Manual Threshold'], 255, cv.THRESH_BINARY)

    # Make the code white so the same morphology works for both polarities
    return cv.bitwise_not(binary), otsu_t  # final: dark code on white, like a printed label


def _worker(jobs, results, parent):
    cv.setNumThreads(1)  # leave the cores to the video loop
    while True:
        try:
            job = jobs.get(timeout=1.0)
        except queue.Empty:
            if os.getppid() != parent:  # reader was killed: don't linger as an orphan
                return
            continue
        if job is None:
            return
        job_id, snapshot = job
        try:
            results.put((job_id, dm_rebuild.rebuild(snapshot), None))
        except Exception as e:  # report, don't die: the main loop is waiting on us
            results.put((job_id, None, repr(e)))


class DecodeWorker:
    """Runs dm_rebuild.rebuild() in a separate process, one snapshot at a time."""

    def __init__(self):
        ctx = mp.get_context('spawn')  # fork + OpenCV/GUI threads can deadlock
        self._jobs = ctx.Queue()
        self._results = ctx.Queue()
        self._proc = ctx.Process(target=_worker, args=(self._jobs, self._results, os.getpid()), daemon=True)
        self._proc.start()
        self._next_id = 0
        self.busy = False

    def submit(self, snapshot):
        """Queue a snapshot; returns its job id, or None if one is still being decoded."""
        if self.busy:
            return None
        self._next_id += 1
        self._jobs.put((self._next_id, snapshot))
        self.busy = True
        return self._next_id

    def poll(self):
        """(job_id, fit, error or None), or None if not done yet."""
        try:
            r = self._results.get_nowait()
        except queue.Empty:
            return None
        self.busy = False
        return r

    def stop(self):
        self._jobs.put(None)
        self._proc.join(timeout=2)
        if self._proc.is_alive():
            self._proc.terminate()
