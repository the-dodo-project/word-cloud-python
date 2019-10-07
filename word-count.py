import nltk, operator, os, re 
from nltk.corpus import stopwords 
import collections
import csv
from random import randrange
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator
import numpy as npy
from PIL import Image

# Path to books converted to .txt
path_to_books = './books/'
# Book files names
book_list = ['biomimicry-chapter1.txt', 
            'sustainability-a-comprehensive-foundation.txt', 
            'sustainable-and-integrated-development-a-critical-analysis.txt',
            'wikipedia-sustainability-entry.txt',
            'sust-bus-models.txt',
            'textbooks-sust-dev.txt',
            'toward-sust-agriculture.txt',
            'sust-global-food.txt']

# Convert .txt book into a list of string tokens
def parse_book_txt_into_tokens():
    tokens = []
    error = 0
    for book in book_list:
        with open(path_to_books + book) as text:
            try:
                lines = text.readlines()
            except UnicodeDecodeError:
                error = error  + 1 

            for line in lines:
                item = line.split()
                tokens.extend(item)

        tokens = [x for x in tokens if x != []]
        text.close()
    return tokens

# Format string tokens
#  - Remove punctuation from words
#  - Convert all to lower case
#  - Revove english stop words
def format_tokens(tokens):

    # Remove punctuation
    tokens_ns = []
    for token in tokens:
        tokens_ns.append(re.sub(r'[^A-Za-z]','',token))

    tokens_low = []
    # convert to lower
    for token in tokens_ns:
        tokens_low.append(token.lower())

    # remove english stop words
    sr = stopwords.words('english')
    sr.append('')
    clean_tokens = tokens_low[:]
    for token in clean_tokens:
        if token in sr:
            clean_tokens.remove(token)

    return clean_tokens

# Identify part-of-speech tagging 
# Note -->  this should have really been done
#           with full sentences rather than with
#           just words. For this purpose, we can 
#           live with it.
def filter_tags(tuples):

    filtered_tags = []
    removed_tokens = []
    # Keep only verbs, nouns, adjetives, adverbs
    tags_to_remove = ['IN', # prepositions
                      'MD', # modal
                      'PRP', 'PRP$', #personal pronoun , possesive pronoun
                      'CD', # cardinal count
                      'DT', # determiner
                      'TO', # to
                      'WP', 'WP$', 'WRB' #wh- words
                      ]
    for t in tuples:
        if t[2] in tags_to_remove:
            removed_tokens.append(t)
        else:
            filtered_tags.append(t)

    return filtered_tags

# Count the ocurrences of each word
def get_token_freq(tokens):
    tuples_list = []
    
    freq = nltk.FreqDist(tokens)

    for key,val in freq.items():
        try:
            tag = nltk.pos_tag(nltk.word_tokenize(key))
            t = (str(key),val,tag[0][1])
            tuples_list.append(t)
        except IndexError:
            pass

    tuples_list.sort(key = operator.itemgetter(1))

    return tuples_list

# Remove additional words manually
#    - Verb to be, have...
#    - ...
def manual_removed(tuples):
    others = ['be','is','are','was','were','been','have','had','has','i','do','not','there','dont',
              'figure','sustainable','sustainability', 'httpcnxorgcontentcol','also','chapter','many',
              'e','p','c','more','other','which','and','bene','however','connexion','connexions','ciency',
              'percent','even','ow','ned','thus','runo','called','cant','part','based','cient'
              'httpcnxorgcontentm', 'total','de','co','ice','most','table','section','ts','eects',
              'often','signi','eg','epa','only','several','due','dierent','much','high','higher',
              'low','lower','speci','rst','less','major','ore', 'small']
    filtered_t = []
    removed_t = []

    for t in tuples:
        if t[0] in others:
            removed_t.append(t)
        else:
            filtered_t.append(t)

    return filtered_t

# Generate tag cloud
def generate_tag_cloud(tuples):
    
    # Create collection (needed for wordcloud)
    word_d = collections.defaultdict(int)
    for t in tuples:
        word_d[t[0]]=int(t[1])
    
    font = "seguihis.ttf"
    font_path_win = "C:\\Windows\\Fonts\\" + font
    
    # The tags will be coloured with our nice blog colour palette
    def colouring_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
        cpalette = ['56baba','469c9e','216869','b7825e','f7931e','cccccc','b3b3b3','999999','666666']
        randc = randrange(len(cpalette))
        r = int(cpalette[randc][:2],16)
        g = int(cpalette[randc][2:4],16)
        b = int(cpalette[randc][-2:],16)
        return "rgb(%d,%d,%d)" % (r,g,b)

    maskArray = npy.array(Image.open("thedodoproject-logo-icon.png"))
    cloud = WordCloud(font_path = font_path_win, background_color = "white", width=2048, height=1152, max_words = 200, color_func=colouring_func, mask = maskArray, contour_color='lightgrey', contour_width=3)
    cloud.generate_from_frequencies(word_d)
    cloud.to_file("word-cloud.png")


# Save tuples in .csv file
def save_in_csv(tuples):
    with open('./results.csv', 'w+') as file:
        for t in tuples:
            file.write(str(t[0]) + ',' + str(t[1]) + ',' + str(t[2]) + '\n')
    file.close()

# Load tuples form .csv file
def load_from_csv():
    with open('./results.csv') as f:
        ts=[tuple(line) for line in csv.reader(f)]
    f.close()

    return ts

# Main program
def main():
    if not os.path.exists('./results.csv'):
        tokens  = parse_book_txt_into_tokens()
        tokens_f = format_tokens(tokens)
        tuples = get_token_freq(tokens_f)
        tuples_f = filter_tags(tuples)
        t_f2 = manual_removed(tuples_f)
        save_in_csv(t_f2[-250:])
        print("Generated .csv with 250 highest frequency words.")

    ''' 
    In this step we have manually stemmed the ~200 words
    with highest frequency. nltk stemmers have not performed so well.
    The list of stemmed words is in "manual-stem.txt".

    NOTE: If the whole program is executed without an exiting 'results.csv'
    file. It will be generated. Stemming step would be missing in this case.
    '''
    t_f3 = load_from_csv()
    # Create tag cloud from just ~200 most frequent
    generate_tag_cloud(t_f3)
    
# Main 
if __name__ == "__main__":
   main()