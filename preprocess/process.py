from spellchecker import SpellChecker
import pandas as pd

spell = SpellChecker()


def check(filepath):
    df = pd.read_csv(filepath)
    for i in range(len(df.columns)):
        for word in df['col' + str(i)]:
            print("pre: " + word)
            word = SpellChecker.correction(self=spell, word=word)
            print("mod: " + word)


check("../source/Tables_Round1/tables/0A1DO6N4.csv")
