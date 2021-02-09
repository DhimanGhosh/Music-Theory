from scipy.spatial.distance import cosine

def string_to_vector(string):
    return [ord(c) for c in string]

s1 = 'suna  man  ka aangan'
s2 = 'Soona Mann Ka Aangan'

v1 = string_to_vector(s1)
v2 = string_to_vector(s2)

cosine_similarity = 1 - cosine(v1, v2)
print(cosine_similarity)
