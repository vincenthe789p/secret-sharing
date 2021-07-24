
dice_word_path = "diceware-words.txt"
alphabet_index_path = "alphabet-index.txt"
def read_dice_to_dict(num_to_word):
    assert type(num_to_word) == dict
    diceware_file = open(dice_word_path, "r")
    while True:
        line = diceware_file.readline()
        if not line:
            break
        num_to_word[line.split()[0]] = line.split()[1]
    diceware_file.close()

def read_alpha_to_dicts(num_to_char, char_to_num):
    assert type(num_to_char) == dict and type(char_to_num) == dict
    alphabet_file = open(alphabet_index_path, "r")
    count = 0
    while True:
        line = alphabet_file.readline()
        if not line:
            break
        num_to_char[count] = line.split()[0]
        char_to_num[line.split()[0]] = count
        count += 1
    alphabet_file.close()
