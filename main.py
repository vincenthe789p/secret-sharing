import ast
import functools
import random
import sys

from converter import *
from scanner import read_alpha_to_dicts
from scanner import read_dice_to_dict



_PRIME = 10007


_RINT = functools.partial(random.SystemRandom().randint, 0)

def _eval_at(poly, x, prime):
    """Evaluates polynomial (coefficient tuple) at x, used to generate a
    shamir pool in make_random_shares below.
    """
    accum = 0
    for coeff in reversed(poly):
        accum *= x
        accum += coeff
        accum %= prime
    return accum

def make_random_shares(secret, minimum, shares, prime=_PRIME):
    """
    Generates a random shamir pool for a given secret, returns share points.
    """
    if minimum > shares:
        raise ValueError("Pool secret would be irrecoverable.")
    poly = [secret] + [_RINT(prime - 1) for i in range(minimum - 1)]
    points = [(i, _eval_at(poly, i, prime))
              for i in range(1, shares + 1)]
    return points

def _extended_gcd(a, b):
    """
    Division in integers modulus p means finding the inverse of the
    denominator modulo p and then multiplying the numerator by this
    inverse (Note: inverse of A is B such that A*B % p == 1) this can
    be computed via extended Euclidean algorithm
    http://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Computation
    """
    x = 0
    last_x = 1
    y = 1
    last_y = 0
    while b != 0:
        quot = a // b
        a, b = b, a % b
        x, last_x = last_x - quot * x, x
        y, last_y = last_y - quot * y, y
    return last_x, last_y

def _divmod(num, den, p):
    """Compute num / den modulo prime p

    To explain what this means, the return value will be such that
    the following is true: den * _divmod(num, den, p) % p == num
    """
    inv, _ = _extended_gcd(den, p)
    return num * inv

def _lagrange_interpolate(x, x_s, y_s, p):
    """
    Find the y-value for the given x, given n (x, y) points;
    k points will define a polynomial of up to kth order.
    """
    k = len(x_s)
    assert k == len(set(x_s)), "points must be distinct"
    def PI(vals):  # upper-case PI -- product of inputs
        accum = 1
        for v in vals:
            accum *= v
        return accum
    nums = []  # avoid inexact division
    dens = []
    for i in range(k):
        others = list(x_s)
        cur = others.pop(i)
        nums.append(PI(x - o for o in others))
        dens.append(PI(cur - o for o in others))
    den = PI(dens)
    num = sum([_divmod(nums[i] * den * y_s[i] % p, dens[i], p)
               for i in range(k)])
    return (_divmod(num, den, p) + p) % p

def recover_secret(shares, prime=_PRIME):
    """
    Recover the secret from share points
    (x, y points on the polynomial).
    """
    if len(shares) < 2:
        raise ValueError("need at least two shares")
    x_s, y_s = zip(*shares)
    return _lagrange_interpolate(0, x_s, y_s, prime)

def main():
    """Main function"""
    assert(len(sys.argv) == 3)
    if (sys.argv[1] == "-codes" and sys.argv[2] == "-gen"):
        total_shares = int(input("Total number of shares to generate: "))
        min_shares = int(input("Minimum number of shares needed to unlock secret: "))
        recovery_code = input("Please input your recovery code char: ")
        if not is_valid_recov_char(recovery_code):
            print("Invalid recovery char")
            return
        num_to_char = {}
        char_to_num = {}
        read_alpha_to_dicts(num_to_char, char_to_num)
        secret = char_to_num[recovery_code]
        shares = make_random_shares(secret, minimum=min_shares, shares=total_shares)
        print('Secret: ',secret)
        print('Shares:')
        if shares:
            for share in shares:
                print('  ', share)

        print("{} shares generated, {} required to unlock secret".format(total_shares, min_shares))
        return
    elif(sys.argv[1] == "-diceware" and sys.argv[2] == "-gen"):
        total_shares = int(input("Total number of shares to generate: "))
        min_shares = int(input("Minimum number of shares needed to unlock secret: "))
        dice_ware_index = input("Please input dice ware index (e.g. 11111): ")
        if not is_valid_dice_index(dice_ware_index):
            print("Invalid dice index")
            return
        
        secret = index_to_decimal(dice_ware_index)
        shares = make_random_shares(secret, minimum=min_shares, shares=total_shares)
        print('Secret: ',secret)
        print('Shares:')
        if shares:
            for share in shares:
                print('  ', share)
        print("{} shares generated, {} required to unlock secret".format(total_shares, min_shares))
        return

    elif(sys.argv[1] == "-diceware" and sys.argv[2] == "-recover"):
        user_input = input("Input shares required to recover diceware as a python list e.g. [(1, 2), (2, 89)]: ")
        shares_list = ast.literal_eval(user_input)
        secret_decimal = recover_secret(shares_list, prime=_PRIME)
        secret_index = decimal_to_index(secret_decimal)
        print("Diceware index: {}".format(secret_index))
        num_to_word = {}
        read_dice_to_dict(num_to_word)
        secret_word = num_to_word[secret_index]
        print("Diceware word: {}".format(secret_word))
        return

    elif(sys.argv[1] == "-codes" and sys.argv[2] == "-recover"):
        user_input = input("Input shares required to recover codes as a python list e.g. [(1, 2), (2, 89)]: ")
        shares_list = ast.literal_eval(user_input)
        secret_decimal = recover_secret(shares_list, prime=_PRIME)

        num_to_char = {}
        char_to_num = {}
        read_alpha_to_dicts(num_to_char, char_to_num)
        secret_char = num_to_char[secret_decimal]
        print("Recovery code char: {}".format(secret_char))
        return

    else:
        print("plz specify proper tags")
        return


if __name__ == '__main__':
    main()