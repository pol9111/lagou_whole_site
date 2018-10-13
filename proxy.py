import random


def bubble_sort(arr):
    length = len(arr)
    for i in range(length-1):
        exchange = 1
        for j in range(length-1-i):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                exchange = 0
        if exchange:
            break


def select_sort(arr):
    length = len(arr)
    for i in range(length-1):
        tmp = i
        for j in range(i+1, length):
            if arr[j] < arr[tmp]:
                tmp = j
        arr[tmp], arr[i] = arr[i], arr[tmp]



def insert_sort(arr):
    length = len(arr)
    for i in range(1, length):
        for j in range(i, 0, -1):
            if arr[j] < arr[j-1]:
                arr[j], arr[j-1] = arr[j-1], arr[j]
            else:
                break


def insertsort(arr):
    length = len(arr)
    gap = length // 2
    while gap > 0:
        for i in range(gap, length):
            j = i
            while j >= gap and arr[j] < arr[j - gap]:
                arr[j], arr[j - gap] = arr[j - gap], arr[j]
                j -= gap
        gap = gap // 2

if __name__ == '__main__':
    l = list(range(100))
    random.shuffle(l)
    print(l)
    insertsort(l)
    print(l)
