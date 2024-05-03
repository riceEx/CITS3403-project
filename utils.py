# check if given word matches with the target word, return an array of 0, 1, 2
# return 0 if the ith letter is not in the target word
# return 1 in cell i if the ith letter is in the word, but in a different place
# return 2 in cell i if the ith letter is in the word and in the right place
def checkWord(sourceWord: str, targetWord: str) -> list[int]:
    result = []
    for i in range(len(sourceWord)):
        if sourceWord[i] == targetWord[i]:
            result.append(2)
        elif sourceWord[i] in targetWord:
            result.append(1)
        else:
            result.append(0)
    return result
