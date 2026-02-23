import random
from collections import Counter

def test_random(begin: int=1, back: int=36, k: int=6, num: int=9) -> None:
    for n, _ in enumerate(range(num), 1):
        test_list = list(range(begin, back+1))
        print(f"Number {n}: {random.choices(test_list, k=k)}")
    
def all_random(begin: int=1, back: int=36, k: int=6, num: int=9) -> None:
    all_list = []
    for n, _ in enumerate(range(num), 1):
        test_list = list(range(begin, back+1))
        all_list.extend(random.choices(test_list, k=k))
    return Counter(all_list).most_common(6)
    
if __name__ == '__main__':
    print(all_random(num=10000000))
    