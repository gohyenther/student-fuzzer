def get_initial_corpus():
    return ["aaaaaaa"]

def entrypoint(s):
    if s == "AAAAAAA":
        print("Found the bug!")
        exit(219)
