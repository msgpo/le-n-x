stopfrags=(
    ('limited',),
    ('article',()),
    ('article',(),(),()),
    )

# german stopwords: http://feya.solariz.de/wp-content/uploads/stopwords.txt
# other languages (also hungarian) can be found here: http://snowball.tartarus.org/algorithms/
# src: http://armandbrahaj.blog.al/2009/04/14/list-of-english-stop-words/
stopwords=['', 'a', 'about', 'above', 'above', 'across', 'after', 'afterwards', 'again',
           'against', 'all', 'almost', 'alone', 'along', 'already',
           'also','although','always','am','among', 'amongst', 'amoungst', 'amount',
           'an', 'and', 'another', 'any','anyhow','anyone','anything','anyway',
           'anywhere', 'are', 'around', 'as',  'at', 'back','be','became',
           'because','become','becomes', 'becoming', 'been', 'before', 'beforehand',
           'behind', 'being', 'below', 'beside', 'besides', 'between', 'beyond', 'bill',
           'both', 'bottom','but', 'by', 'call', 'can', 'cannot', 'cant', 'co', 'con',
           'could', 'couldnt', 'cry', 'de', 'describe', 'detail', 'do', 'done', 'down',
           'due', 'during', 'each', 'eg', 'eight', 'either', 'eleven','else', 'elsewhere',
           'empty', 'enough', 'etc', 'even', 'ever', 'every', 'everyone', 'everything',
           'everywhere', 'except', 'few', 'fifteen', 'fify', 'fill', 'find', 'fire',
           'first', 'five', 'for', 'former', 'formerly', 'forty', 'found', 'four', 'from',
           'front', 'full', 'further', 'get', 'give', 'go', 'had', 'has', 'hasnt', 'have',
           'he', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon',
           'hers', 'herself', 'him', 'himself', 'his', 'how', 'however', 'hundred', 'ie',
           'if', 'in', 'inc', 'indeed', 'interest', 'into', 'is', 'it', 'its', 'itself',
           'keep', 'last', 'latter', 'latterly', 'least', 'less', 'ltd', 'made', 'many',
           'may', 'me', 'meanwhile', 'might', 'mill', 'mine', 'more', 'moreover', 'most',
           'mostly', 'move', 'much', 'must', 'my', 'myself', 'name', 'namely', 'neither',
           'never', 'nevertheless', 'next', 'nine', 'no', 'nobody', 'none', 'noone',
           'nor', 'not', 'nothing', 'now', 'nowhere', 'of', 'off', 'often', 'on', 'once',
           'one', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'our', 'ours',
           'ourselves', 'out', 'over', 'own','part', 'per', 'perhaps', 'please', 'put',
           'rather', 're', 'same', 'see', 'seem', 'seemed', 'seeming', 'seems', 'serious',
           'several', 'she', 'should', 'show', 'side', 'since', 'sincere', 'six', 'sixty',
           'so', 'some', 'somehow', 'someone', 'something', 'sometime', 'sometimes',
           'somewhere', 'still', 'such', 'system', 'take', 'ten', 'than', 'that', 'the',
           'their', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter',
           'thereby', 'therefore', 'therein', 'thereupon', 'these', 'they', 'thickv',
           'thin', 'third', 'this', 'those', 'though', 'three', 'through', 'throughout',
           'thru', 'thus', 'to', 'together', 'too', 'top', 'toward', 'towards', 'twelve',
           'twenty', 'two', 'un', 'under', 'until', 'up', 'upon', 'us', 'very', 'via',
           'was', 'we', 'well', 'were', 'what', 'whatever', 'when', 'whence', 'whenever',
           'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon',
           'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole',
           'whom', 'whose', 'why', 'will', 'with', 'within', 'without', 'would', 'yet',
           'you', 'your', 'yours', 'yourself', 'yourselves',
           'shall', "Europa", "European", "states", "quot", "gt", "directive",
           "member", "article" ]
# remove single digits
stopwords+=[str(x) for x in range(0,10)]
# remove single chars
stopwords+=[chr(x) for x in range(ord('a'),ord('z'))+range(ord('A'),ord('Z'))]

class StopFrags():
    def __init__(self):
        #TODO db for stopfrags?
        self.stopFrags = stopfrags
