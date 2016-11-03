'''
@author: Linxi Fan (lf2422)
CKY algorithm
'''
from __future__ import division, print_function
import json, math, sys, re

from nltk import tree, treetransforms
from copy import deepcopy

log = math.log10

unary = {}  # unary rules
binary = {} # binary rules
nonterm = {} # non-terminals that will lead a binary rule
counts = {} # count the number of terminals (words) to decide <unk>

# populate the counts
for line in open(sys.argv[1], 'r'): # real_count
    entries = line.strip().split(' ')
    typ = entries[1]
    n = int(entries[0])
    if typ == 'NON-TER':
        nonterm[entries[2]] = n
    elif typ == 'BI-RULE':
        binary[tuple(entries[2:])] = n
    elif typ == 'UN-RULE':
        unary[tuple(entries[2:])] = n
        word = entries[3]
        if not word in counts:
            counts[word] = n
        else:
            counts[word] += n


NEG_INFN = -10000 # log probability negative infinity

# log probability
# Here 'nt' is the first-level nonterminal: either a mega-tag (with '+') or a POS tag
def emissionP(nt, word):  # log of q(NTs -> word)
    if counts.get(word, 0) < 5:
        word = '<unk>'
    if not (nt, word) in unary:
        return NEG_INFN
    else:
        return log(unary[nt, word] / nonterm[nt])

def bruleP(*rule): # log of q(X -> Y1 Y2)
    # 'rule' is a 3-tuple (X, Y, Z)
    if not rule in binary:
        return NEG_INFN
    else:
        return log(binary[rule] / nonterm[rule[0]])

# brules[X] = [ all (Y, Z) binary rule tuples ]
brules = {}
for rule in binary:
    if not rule[0] in brules:
        brules[rule[0]] = [tuple(rule[1:])]
    else:
        brules[rule[0]].append(tuple(rule[1:]))


# Parses a sentence with words separated by space
# returns a list that represents the parse tree
def parse(sen):
  try:
    sen = sen.split(' ')
    n = len(sen)

    # All powerful pi table and its backpointers
    pi = [[{} for i in range(n)] for j in range(n)] # pi[i][j][ROOT] = prob
    bp = [[{} for i in range(n)] for j in range(n)] # bp[i][j][ROOT] = (binary_rule, split_point s)

    # Initialize
    for i in range(n):
        # Emission prob involves only the unaryRule NTs. Other NTs will be filled to 0
        for X in nonterm:
            pi[i][i][X] = emissionP(X, sen[i])
            bp[i][i][X] = sen[i]

    # Recursively fill out the tables
    for dist in range(1, n):
        for i in range(n - dist):
            j = i + dist  # distance between i and j
                        # Distance 0 are already filled out at Init stage
                        # We then fill out distance 1 between all (i, j) pairs, then distance 2, etc.
            # set of NTs that are able to lead binary rules
            for X in brules:
                # max with respect to a binary YZ and a split point
                mx = NEG_INFN
                bestarg = i, None, None  # stores the split point and the best binrule
                for s in range(i, j):
                    for (Y, Z) in brules[X]: # YZ is the tuple for which X -> Y Z
                        prob = bruleP(X, Y, Z) + pi[i][s].get(Y, NEG_INFN) + pi[s+1][j].get(Z, NEG_INFN)
                        if prob > mx:
                            mx = prob
                            bestarg = s, Y, Z
                # fill out the pi and backpointer table
                pi[i][j][X] = mx
                bp[i][j][X] = bestarg

    # Retrieve the tree from backpointers
    if pi[0][n-1].get('TOP', NEG_INFN) > NEG_INFN:
        return getParseTree(bp, 0, n - 1, 'TOP')
    else: # final iteration to determine the ROOT with largest probability
        mx = NEG_INFN
        root = 'TOP'
        for X in brules:
            prob = pi[0][n-1].get(X, NEG_INFN)
            if prob > mx:
                mx = prob
                root = X
        return getParseTree(bp, 0, n - 1, root)
  except:
    return ""



# Given a filled out backpointer table, recover the parse tree as a nested list
# root = 'S' except for sentence fragments
def getParseTree(bp, i, j, root):
    # If i and j points to one place, return that terminal (word) and its unary tag
    if i == j:  return [root, bp[i][i][root]]
    s, Y, Z = bp[i][j][root] # retrieve split point and YZ
    return [root, getParseTree(bp, i, s, Y), getParseTree(bp, s+1, j, Z)]


# Main: IO and JSON output
if __name__ == '__main__':
    i = 0 # progress tracker
    for sen in open(sys.argv[2], 'r'): # parse_dev.dat

        try:
            answer = str(json.dumps(parse(sen.strip())))
            answer = answer.replace("[","(")
            answer = answer.replace("]",")")
            answer = answer.replace(",","")
            answer = answer.replace('"','')

            t = tree.Tree.fromstring(answer, remove_empty_top_bracketing=True)
            answer = deepcopy(t)
            treetransforms.un_chomsky_normal_form(answer)

            answer = answer.__str__()
            answer = answer.replace("\n","")
            answer = re.sub(' +',' ',answer)

            print(answer)

        except:
            print("error")

#    print('DONE: {0} sentences'.format(i), file=sys.stderr)
