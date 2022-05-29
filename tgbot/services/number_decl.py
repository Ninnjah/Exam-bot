from typing import List, Union


def get_declination(num: Union[float, int], string: List[str]):
    num = num % 100

    if 11 <= num <= 19:
        declined_num = string[2]

    else:
        i = num % 10
        if i == 1:
            declined_num = string[0]
        elif i in [2, 3, 4]:
            declined_num = string[1]
        else:
            declined_num = string[2]

    return declined_num
