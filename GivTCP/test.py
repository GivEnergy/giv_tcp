import pickle
with open("test.pkl", 'rb') as inp:
    previousUpdate= pickle.load(inp)
print (str(previousUpdate))