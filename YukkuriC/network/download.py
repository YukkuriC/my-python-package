"""通用多线程分片 + 断点续传下载。

流程：
    1. 探测远端是否支持 Range 并获取文件总大小
    2. 支持且文件足够大时按线程数分片并行下载，分片缓存在 cache_dir，
       中断后重新调用即可从已下载字节处续传
    3. 不支持 Range 或文件过小时退化为单线程续传
"""
import json
import os
import shutil
import sys
import threading
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TIMEOUT = 15
THREADS = 8
PART_MIN_SIZE = 100 * 1024
READ_SIZE = 64 * 1024


def filename_from_url(url):
    """取 URL 路径末段作为文件名，缺失时抛 ValueError。"""
    name = urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit('/', 1)[-1])
    if not name:
        raise ValueError(f'无法从 URL 推断文件名: {url}')
    return name


def _cache_dir_for(dest):
    return dest.parent / f'.dl_{dest.name}'


def probe_range(url, timeout=TIMEOUT):
    """探测文件总大小与服务器是否支持 Range。

    返回 (总大小或 None, 是否支持 Range)。仅支持 Range 时总大小才可用于分片。
    """
    req = urllib.request.Request(url, headers={'Range': 'bytes=0-0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 206:
            return None, False
        content_range = resp.headers.get('Content-Range', '')
        try:
            return int(content_range.rsplit('/', 1)[-1]), True
        except ValueError:
            return None, False


def split_ranges(total, threads=THREADS, part_min_size=PART_MIN_SIZE):
    """按线程数把 [0, total) 切分为若干分片区间，每片不小于 part_min_size。"""
    parts = max(1, min(threads, total // part_min_size))
    size = total // parts
    ranges = []
    start = 0
    for i in range(parts):
        end = total if i == parts - 1 else start + size
        ranges.append([start, end])
        start = end
    return ranges


class _Progress:
    def __init__(self, total, done=0):
        self.total = total
        self.done = done
        self.lock = threading.Lock()

    def add(self, n):
        with self.lock:
            self.done += n
            percent = min(100, self.done * 100 // self.total)
            sys.stdout.write(f'\r  下载进度: {percent}% ({self.done}/{self.total} bytes)')
            sys.stdout.flush()


def download_part(url, start, end, path, progress, stop, timeout=TIMEOUT):
    """下载分片 [start, end)，已存在的字节视为已下载，从而支持断点续传。"""
    path = Path(path)
    have = path.stat().st_size if path.exists() else 0
    if have >= end - start:
        return
    req = urllib.request.Request(
        url, headers={'Range': f'bytes={start + have}-{end - 1}'}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(path, 'ab') as f:
        if resp.status != 206:
            raise RuntimeError(f'分片 {start}-{end} 未返回 206')
        while not stop.is_set():
            chunk = resp.read(READ_SIZE)
            if not chunk:
                break
            f.write(chunk)
            progress.add(len(chunk))


def download_multi(url, dest, total, cache_dir=None, threads=THREADS, timeout=TIMEOUT):
    """多线程分片下载，分片与元数据缓存在 cache_dir，支持断点续传。

    cache_dir 默认取目标文件旁的 .dl_<文件名>/。
    """
    dest = Path(dest)
    cache_dir = Path(cache_dir) if cache_dir is not None else _cache_dir_for(dest)
    meta_path = cache_dir / 'meta.json'
    ranges = split_ranges(total, threads)
    meta = {'url': url, 'total': total, 'ranges': ranges}

    if meta_path.exists():
        try:
            cached = json.loads(meta_path.read_text(encoding='utf-8'))
        except ValueError:
            cached = None
        if cached != meta:
            print('  缓存的文件信息不匹配，丢弃旧分片')
            shutil.rmtree(cache_dir, ignore_errors=True)

    cache_dir.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta), encoding='utf-8')

    part_paths = [cache_dir / f'part{i}' for i in range(len(ranges))]
    resumed = sum(
        min(p.stat().st_size, e - s)
        for p, (s, e) in zip(part_paths, ranges)
        if p.exists()
    )
    if resumed:
        print(f'  发现已下载数据 {resumed} bytes，继续续传')

    progress = _Progress(total, resumed)
    stop = threading.Event()
    print(f'  分片数: {len(ranges)}')
    try:
        with ThreadPoolExecutor(max_workers=len(ranges)) as pool:
            futures = [
                pool.submit(download_part, url, s, e, p, progress, stop, timeout)
                for (s, e), p in zip(ranges, part_paths)
            ]
            for future in futures:
                future.result()
    except KeyboardInterrupt:
        stop.set()
        sys.stdout.write('\n')
        print('已中断，分片已保留，重新调用即可续传')
        raise

    sys.stdout.write('\n')
    if sum(p.stat().st_size for p in part_paths) != total:
        raise RuntimeError('分片总大小与远端文件大小不一致')

    tmp_out = dest.parent / (dest.name + '.tmp')
    with open(tmp_out, 'wb') as out:
        for p in part_paths:
            with open(p, 'rb') as f:
                shutil.copyfileobj(f, out)
    os.replace(tmp_out, dest)
    shutil.rmtree(cache_dir, ignore_errors=True)
    return dest


def download_single(url, dest, timeout=TIMEOUT):
    """单线程下载；服务器支持 Range 时按已下载字节续传。"""
    dest = Path(dest)
    tmp = dest.parent / (dest.name + '.tmp')
    have = tmp.stat().st_size if tmp.exists() else 0
    if have:
        print(f'  发现未完成文件 {have} bytes，尝试续传')
    req = urllib.request.Request(
        url, headers={'Range': f'bytes={have}-'} if have else {}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if have and resp.status != 206:
            print('  服务器不支持 Range，从头下载')
            have = 0
        total = int(resp.headers.get('Content-Length') or 0) + have
        progress = _Progress(total, have)
        with open(tmp, 'ab' if have else 'wb') as f:
            while True:
                chunk = resp.read(READ_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                progress.add(len(chunk))
    sys.stdout.write('\n')
    os.replace(tmp, dest)
    return dest


def download(url, dest=None, cache_dir=None, threads=THREADS, timeout=TIMEOUT):
    """下载 url 到 dest（默认取 URL 末段为文件名），返回目标路径。"""
    dest = Path(filename_from_url(url) if dest is None else dest)
    print(f'下载: {url}')
    print(f'保存: {dest}')
    total, ranged = probe_range(url, timeout)
    if ranged and total and total >= PART_MIN_SIZE:
        download_multi(url, dest, total, cache_dir, threads, timeout)
    else:
        print('  远端不支持 Range 或文件过小，使用单线程下载')
        download_single(url, dest, timeout)
    return dest


__all__ = [
    'TIMEOUT',
    'THREADS',
    'PART_MIN_SIZE',
    'filename_from_url',
    'probe_range',
    'split_ranges',
    'download_part',
    'download_multi',
    'download_single',
    'download',
]
