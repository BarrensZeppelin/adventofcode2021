from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict, deque
from functools import lru_cache, total_ordering
from heapq import *
from itertools import combinations
from itertools import combinations_with_replacement as combr
from itertools import cycle, permutations, product, repeat
from typing import (Any, Callable, Collection, DefaultDict, Dict, Generic,
                    Iterable, Iterator, List, Mapping, MutableSet, Sequence,
                    Tuple, TypeVar)

sys.setrecursionlimit(1 << 30)

DIR = ((1, 0), (0, 1), (-1, 0), (0, -1))


def ints(inp: str = None) -> Iterator[int]:
    return map(int, re.findall(r"-?\d+", inp or sys.stdin.read()))


def floats(inp: str = None) -> Iterator[float]:
    return map(float, re.findall(r"-?\d+(?:\.\d*)?", inp or sys.stdin.read()))


def lines(inp: str = None) -> List[str]:
    return (inp or sys.stdin.read()).splitlines()


def prints(*args):
    """
    Function for printing the solution to a puzzle.
    Also copies the solution to the clipboard.
    """
    from subprocess import run

    ans = " ".join(map(str, args))
    print(ans)
    run(["xsel", "-bi"], input=ans, check=True, text=True)
    print("(Copied to clipboard)")


T = TypeVar("T", int, float)


def sign(x: T) -> int:
    return (x > 0) - (x < 0)


@total_ordering
class Point(Generic[T]):
    c: List[T]
    __slots__ = ("c",)

    def __init__(self, c: List[T]):
        self.c = c

    @classmethod
    def of(cls, *c: T) -> Point[T]:
        return cls(list(c))

    # Points are generally immutable except that you can set coordinates

    @property
    def x(s) -> T:
        return s.c[0]

    @x.setter
    def x(s, v: T):
        s.c[0] = v

    @property
    def y(s) -> T:
        return s.c[1]

    @y.setter
    def y(s, v: T):
        s.c[1] = v

    @property
    def z(s) -> T:
        return s.c[2]

    @z.setter
    def z(s, v: T):
        s.c[2] = v

    # Standard object methods

    def __lt__(s, o: Point[T]) -> bool:
        return s.c < o.c

    def __eq__(s, o) -> bool:
        return isinstance(o, Point) and s.c == o.c

    def __hash__(s) -> int:
        return hash(tuple(s.c))

    def __str__(s) -> str:
        return f'({", ".join(map(str, s))})'

    def __repr__(s) -> str:
        return f"Point({s.c})"

    def __len__(s) -> int:
        return len(s.c)

    def __iter__(s) -> Iterator[T]:
        return iter(s.c)

    def __getitem__(s, key):
        return s.c[key]

    # Geometry stuff

    def __add__(s, o: Iterable[T]) -> Point[T]:
        return Point([a + b for a, b in zip(s, o)])

    def __sub__(s, o: Iterable[T]) -> Point[T]:
        return Point([a - b for a, b in zip(s, o)])

    def __neg__(s) -> Point[T]:
        return Point([-x for x in s])

    def __abs__(s) -> Point[T]:
        return Point.of(*map(lambda x: abs(x), s))

    def __mul__(s, d: T) -> Point[T]:
        return Point([a * d for a in s])

    __rmul__ = __mul__

    def __floordiv__(s, d: T) -> Point[T]:
        return Point([a // d for a in s])

    def __truediv__(s, d: T) -> Point[float]:
        return Point([a / d for a in s])

    def dot(s, o: Iterable[T]) -> T:
        return sum(a * b for a, b in zip(s, o))

    __matmul__ = dot

    def cross(a, b: Point[T]) -> T:
        assert len(a) == 2
        return a.x * b.y - a.y * b.x

    def cross2(s, a: Point[T], b: Point[T]) -> T:
        return (a - s).cross(b - s)

    def cross_3d(a, b: Point[T]) -> Point[T]:
        assert len(a) == 3
        return Point.of(
            a.y * b.z - a.z * b.y, -a.x * b.z + a.z * b.x, a.x * b.y - a.y * b.x
        )

    def cross2_3d(s, a: Point[T], b: Point[T]) -> Point[T]:
        return (a - s).cross_3d(b - s)

    def manh_dist(s) -> T:
        return sum(map(lambda x: abs(x), s))

    def dist2(s) -> T:
        return sum(x * x for x in s)

    def dist(s) -> float:
        return s.dist2() ** 0.5


def make_adj(edges, both=False) -> DefaultDict[Any, List]:
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
        if both:
            adj[b].append(a)
    return adj


def make_wadj(edges, both=False) -> DefaultDict[Any, List[Tuple[Any, Any]]]:
    adj = defaultdict(list)
    for a, b, w in edges:
        adj[a].append((b, w))
        if both:
            adj[b].append((a, w))
    return adj


def bfs(s, adj):
    D: DefaultDict[Any, float] = defaultdict(lambda: float("inf"))
    D[s] = 0
    Q = [s]
    for i in Q:
        d = D[i]
        for j in adj[i]:
            if j in D:
                continue
            D[j] = d + 1
            Q.append(j)
    return D, Q


def dijkstra(s, adj):
    D: DefaultDict[Any, float] = defaultdict(lambda: float("inf"))
    V = set()
    D[s] = 0
    Q = [(0, s)]
    while Q:
        d, i = heappop(Q)
        if i in V:
            continue
        V.add(i)
        for j, w in adj[i]:
            if j in V:
                continue
            nd = d + w
            if nd >= D[j]:
                continue
            D[j] = nd
            heappush(Q, (nd, j))
    return D


def topsort(adj):
    indeg: DefaultDict[Any, int] = defaultdict(int)
    for i, l in adj.items():
        for j in l:
            indeg[j] += 1
    Q = [i for i in adj if indeg[i] == 0]
    for i in Q:
        for j in adj[i]:
            indeg[j] -= 1
            if indeg[j] == 0:
                Q.append(j)
    return Q


_U = TypeVar("_U")


def tile(L: Sequence[_U], S: int) -> List[Sequence[_U]]:
    assert len(L) % S == 0
    return [L[i : i + S] for i in range(0, len(L), S)]


def print_coords(L: Collection[Tuple[int, int]], empty = ' '):
    import collections.abc

    xs, ys = zip(*L)
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    print("X", min_x, max_x)
    print("Y", min_y, max_y)

    R = [[empty] * (max_x - min_x + 1) for _ in range(max_y - min_y + 1)]

    if isinstance(L, collections.abc.Mapping):
        for (x, y), c in L.items():
            assert len(c) == 1, ((x, y), c)
            R[y - min_y][x - min_x] = c
    else:
        for x, y in L:
            R[y - min_y][x - min_x] = "#"

    print(*map("".join, R), sep="\n")


def binary_search(f: Callable[[int], bool], lo: int, hi: int = None) -> int:
    " Returns the first i >= lo such that f(i) == True "
    if hi is None:
        assert lo >= 0
        hi = lo + 1
        while not f(hi):
            lo, hi = hi, hi * 2

    assert lo <= hi
    while lo < hi:
        m = (lo + hi) // 2
        if f(m):
            hi = m
        else:
            lo = m + 1

    return lo


def neighbours(
    x: int, y: int, dirs: Iterable[Tuple[int, int]] = DIR, V=None
) -> Iterator[Tuple[int, int]]:
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if V is None or (nx, ny) in V:
            yield nx, ny
