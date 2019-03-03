import numpy as np
import matplotlib.pyplot as plt

text_length = 100
short_word = 3
long_word = 5
alphabet = [chr((ord('a')+i)) for i in range(0, 26)] + ["abacaba"]
frequency = np.array([1, 10, 10, 5, 2, 2, 2, 1, 10, 5, 8, 4, 8, 7, 2, 9, 9, 9, 1, 9, 2, 1, 1, 10, 3, 1, 10])
frequency = frequency[:len(alphabet)]
frequency = frequency / np.sum(frequency)
occ = np.ceil((text_length * frequency)).astype(int)

"""
    Tato část lze použít pro generování náhodné distribuce frekvence písmen. Nahradí fixni frekvenci [frequency].
    V případě potřeby lze odkomentováním i vykreslit histogram počtů výskytů písmen.
"""
# # Minimální a maximální počet od jednoho znaku v jedné sadě znaků. (Ty jsou ale následně propermutovány)
# mmin = 1
# mmax = 10
# # Funkce distribuce počtů výskytů. Vrací pravděpodobnost, že se číslo bude v jedné sadě vyskytovat n-krát
# def dist_function(x):
#     return (x-mmin-mmax/2)**2 + 0.5

# distribution = [ dist_function(i) for i in range(mmin, mmax+1) ] # normalizace pravděpodobnostní distibuce, aby se jednalo o probabilistický vektor (tedy součet byl 1)
# distribution = distribution / np.sum(distribution)
# f = [np.random.choice(list(range(mmin, mmax+1)), None, True, distribution) for _ in alphabet] # Podle zadané pravděpodobnosti distibuce náhodně vybere fixní počet v jedné sadě pro každý znak
# # plt.hist(f)
# # plt.show()

"""
Samotné generování textu. Nejdříve se vygeneruje dostatečně dlouhý text s počtem znaků odpovídajícím poli [occ]. Následně se propermutuje a rozdělí mezerami.
"""
text = sum([[alphabet[i]] * occ[i] for i in range(len(alphabet))], []) # Vygeneruje jednu sadu obsahující příslušný počet výskytů pro každý znak
text = "".join(np.random.permutation(text)) # Propermutuje sadu znaků
spaces = np.random.permutation(sum([[short_word, long_word] for i in range(len(text)//(short_word+long_word))], [])) # Vygeneruje náhodnou posloupnost vzdáeností mezer od sebe
final_text = "".join([ text[sum(spaces[:i]):sum(spaces[:i])+spaces[i]]+" " for i in range(len(spaces)) ]) # Rozdělí text mezerami podle pole [spaces]

print("Final text: {0}".format(final_text))
print("Final text length: {0}".format(len(final_text)))

"""
Přepočítání a vykreslení počtu výskytů jednotlivých znaků.
"""
def compute_frequency(data):
    frequency = {}
    for d in data:
        if d not in frequency:
            frequency[d] = 0
        frequency[d] += 1
    return list(zip(*sorted(frequency.items())))

x1, y1 = compute_frequency(final_text)
plt.subplot(211)
plt.bar(x1, y1)
x2, y2 = compute_frequency(y1)
plt.subplot(212)
plt.bar(x2, y2)
plt.show()