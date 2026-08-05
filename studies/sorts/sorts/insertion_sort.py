def insertion_sort(S: list) -> tuple:
    comparisons: int = 0

    for i in range(1, len(S)):
        temp = S[i]

        j = i - 1
        while j >= 0:
            comparisons += 1

            if S[j] > temp:
                S[j + 1] = S[j]
                j -= 1
            else:
                break
        S[j + 1] = temp
    return (comparisons, S)


"""
Input: A sequence S to be sorted
Result: A modified S array and comparison count

for i: 0 -> S.length:
    temp = a[i]

    // slide down elements to make room for a[i]
    int j = i
    while (j > 0 && a[j - 1] > temp) {
        a[j] = a[j - 1];
        j--;
    }
    a[j] = temp;
"""
