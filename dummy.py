def comb(t):
    n = len(t)
    cnt = (1 << n)
    print 'tuple: %s, length: %d, combination count: %d' % (t, n, cnt)
    for i in xrange(cnt):
        tmp = []
        for j in xrange(n):
            if (1 << j) & i != 0:
                tmp.append(t[j])
        yield tmp


if __name__ == "__main__":
    t = (1, 2)
    for r in comb(t):
        print r

    print "****" * 5

    t = (1,2,3)
    for r in comb(t):
        print r
    print "****" * 5

    t = (1,2,3,4,5,6,7,8)
    for r in comb(t):
        print r
