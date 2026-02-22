def min_diff_map(list1, list2):
    size1, size2 = len(list1), len(list2)
    grid = [[(0, 'end')] * (size2 + 1) for _ in range(size1 + 1)]

    # dp
    for i in range(size1):
        grid[1 + i][0] = (i + 1, 'del')
    for i in range(size2):
        grid[0][1 + i] = (i + 1, 'add')
    for i, elem1 in enumerate(list1):
        i += 1
        for j, elem2 in enumerate(list2):
            j += 1
            score, op = min(
                (grid[i][j - 1][0] + 1, 'add'),
                (grid[i - 1][j][0] + 1, 'del'),
            )
            if elem1 == elem2:
                score, op = min(
                    (score, op),
                    (grid[i - 1][j - 1][0], 'cpy'),
                )
            grid[i][j] = (score, op)

    return grid


def min_diff_seq(list1, list2):
    grid = min_diff_map(list1, list2)
    ptr1, ptr2 = len(list1), len(list2)

    res = []
    while ptr1 and ptr2:
        op = grid[ptr1][ptr2][1]
        if op == 'add':
            ptr2 -= 1
            res.append((op, list2[ptr2]))
        elif op == 'del':
            ptr1 -= 1
            res.append((op, list1[ptr1]))
        elif op == 'cpy':
            ptr1 -= 1
            ptr2 -= 1
            res.append((op, list1[ptr1]))
        else:
            raise op

    res.reverse()
    return res


if __name__ == '__main__':
    l1 = '114514'
    l2 = '1919810'
    print(min_diff_seq(l1, l2))

__all__ = ['min_diff_seq']
