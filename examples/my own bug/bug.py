def get_initial_corpus():
    return ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]


def entrypoint(s):
    x = 0
    if len(s) > 2 and s[2] == 'B':
        if len(s) > 3 and s[3] == 'A':
            if len(s) > 4 and s[4] == 'D':
                if len(s) > 5 and s[5] == '!':
                    print("Found the bug!")
                    exit(219)
