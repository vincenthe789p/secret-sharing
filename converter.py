import re

ERROR = -666
def is_valid_dice_index(index_str):
    index_pattern = r'^[1-6]{5}$'
    return re.fullmatch(index_pattern, index_str)

def is_valid_recov_char(char):
    char_pattern = r'^[A-Z0-9]$'
    return re.fullmatch(char_pattern, char)



def base6_to_dec(num):
    if num == 0:
        return 0
    num = str(num)
    ans = int(num[0])
    for i in num[1:]:
        ans *= 6
        ans += int(i)
    return ans

def dec_to_base6(num):
    if num == 0:
        return 0
    ans = ""
    while num > 0:
        ans = str(num%6) + ans
        num //= 6
    return int(ans)

def index_to_decimal(index):
    index_str = str(index)
    
    if not is_valid_dice_index(index_str):
        raise Exception
    index_str_minus_one = ""
    for i in range(5):
        index_str_minus_one += str(int(index_str[i]) - 1)
    
    return base6_to_dec(int(index_str_minus_one))


def decimal_to_index(decimal):
    if decimal >= 7776 or decimal < 0:
        return ERROR
    base6_num = dec_to_base6(decimal)
    base6_str_zero_fill = "{:05d}".format(base6_num)
    index_str_plus_one = ""
    for i in range(5):
        index_str_plus_one += str(int(base6_str_zero_fill[i]) + 1)
    
    return str(index_str_plus_one)

def tester():
    for i in range(0, 7776):
        assert(index_to_decimal(decimal_to_index(i)) == i )
