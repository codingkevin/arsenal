from arsenal.datastructures.heap import MaxHeap
from arsenal.iterextras import buf_iter, head_iter
from heapq import heapify, heappop, _siftup


def sorted_union(*iterators):
    """
    Merge multiple sorted inputs into a single sorted output.

    Equivalent to:  sorted(itertools.chain(*iterables))

    >>> list(merge_sorted([1,3,5,7], [0,2,4,8], [5,10,15,20], [], [25]))
    [0, 1, 2, 3, 4, 5, 5, 7, 8, 10, 15, 20, 25]
    """

    h = [head_iter(s) for s in iterators]
    h = [s for s in h if not s.done]
    heapify(h)
    while h:
        s = h[0]
        yield s.__next__()       # advance the top iterator
        if s.done:
            heappop(h)           # remove empty iterator
        else:
            _siftup(h, 0)        # restore heap condition

merge_sorted = sorted_union


class Item:
    def __init__(self, score, index, elems):
        self.score = score
        self.index = index
        self.elems = elems
    def __lt__(self, other):
        # Note: reversed
        return self.score > other.score
    def __le__(self, other):
        # Note: reversed
        return self.score > other.score or self.score == other.score


def sorted_product(p, *iters):
    """
    Sorted product of `iters`, where the output is sorted by a monotonic product
    operator `p`.  Examples: tuples, or multiplication/addition of positive numbers.
    """

    n = len(iters)
    assert n > 1

    # use buffered iterator to ensure (random) access to the previously emitted
    # values of each iterator.
    iters = [buf_iter(it) for it in iters]

    def vals(z):
        return tuple(it[j] for it, j in zip(iters, z))

    # elements in the heap are wrapped `Item` to make it a min heap.
    q = MaxHeap()
    y = (0,)*n
    q.push(Item(p(vals(y)), 0, y))

#    from collections import Counter
#    pushes = Counter()


    while q:  # this line is slightly wrong due to a bug in prioritydict

        item = q.pop()
        x = item.elems
        j = item.index

        yield item.score

        # next best item must differ by one, enqueue all such items
        # We reduce the number of pushes by the dotted rule trick.
        for i in range(j, n):

            y = list(x)
            y[i] = x[i] + 1
            y = tuple(y)

            #if x[i] + 1 >= len(a[i]): continue
            try:
                iters[i][y[i]]
            except IndexError:
                # `IndexError` is thrown when `iter[i]` is finite and we
                # requested more iterates than it has.
                continue

            # Efficiency improvement: memoize the prefix/suffix products to save
            # on the cost of p here.  We know that it differs from the priority
            # of the emitted `p(vals(x))` in only position `i`.
            #
            # Are there other tricks to reduce the number of pushes?
            q.push(Item(p(vals(y)), i, y))

#            pushes[y] += 1

#    print('PUSHES BY ITEM:', {k:v for k,v in pushes.items() if v > 1})
#    print('TOTAL PUSHES:', sum(pushes.values()))



def main():
    import numpy as np
    import itertools
    from arsenal.iterextras import take
    from itertools import count


    # weighted tuples are the idea as a path weight with backpointers; our weighted
    # tuple copies the tuple, so it is inefficient compared to the lazier
    # backpointer variant.
    class WeightedTuple:
        def __init__(self, w, *key):
            self.key = key
            self.w = w
        def __lt__(self, other):
            return (self.w, self.key) < (other.w, other.key)
        def __eq__(self, other):
            return (self.w, self.key) == (other.w, other.key)
        def __mul__(self, other):
            return LWeightedTuple(self.w*other.w, self, other)
        def __add__(self, other):
            return LWeightedTuple(self.w+other.w, self, other)
        def __iter__(self):
            return iter((self.w, self.key))
        def __repr__(self):
            return repr((self.w, self.key))


    class LWeightedTuple(WeightedTuple):
        "WeightedTuple with lazy concatenation of keys."
        def __init__(self, w, a, b):
            self.w = w
            self.a = a
            self.b = b
        @property
        def key(self):
            return self.a.key + self.b.key


    def wprod(xs):
        return np.product([WeightedTuple(x, x) for x in xs])

    def wsum(xs):
        return np.sum([WeightedTuple(x, x) for x in xs])

    def check(iters):
        for p in [np.product, np.sum, tuple, wprod]:
            # enumerate and sort; not lazy
            want = list(sorted(p(x) for x in itertools.product(*iters)))
            got = list(sorted_product(p, *iters))
            print()
            print('product operator:', p.__name__)
            print('GOT:', got)
            #if got != want:
            print('WANT:', want)
            assert got == want
        print('pass.')

    print('===========')
    check([
        (.1, .4, 0.5),
        (0.09, 0.11, 0.8),
        (0.111, .3, 0.6),
    ])
    print('===========')
    check([
        (1, 2, 3),
        (4, 7, 11),
    ])
    print('===========')
    check([
        (0.01, .4, 0.5),
        (0.11, 0.8),
        (0.6,),
    ])
    print('===========')
    check([
        (1, 2, 3, 100),
        (4, 7, 9),
        (14, 17, 19),
        (24, 27, 29),
    ])
    print('===========')


    a = (3**i for i in count(1))
    b = (4**i for i in count(1))
    c = (5**i for i in count(1))

    for s,x in take(20, sorted_product(wsum, a, b, c)):
        print(s, x)


if __name__ == '__main__':
    main()
