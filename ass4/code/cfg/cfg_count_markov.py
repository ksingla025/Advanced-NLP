#!/usr/bin/python

import sys, json, re
from collections import Counter
from nltk import tree, treetransforms
from copy import deepcopy

"""
Count rule frequencies in a binarized CFG.
"""

'''Usage: python count_cfg_freq.py [tree_file]'''

class Counts(object):
  def __init__(self):
    self.mapping = {}
    for line in open("en.map","r"):
        line=line.strip()
        spl=line.split()
        self.mapping[spl[0]]=spl[1]

    self.unary = {}
    self.binary = {}
    self.nonterm = {}

  def show(self):
    for symbol, count in self.nonterm.iteritems():
      print count, "NON-TER", symbol
    rule_dic = {}

    for (sym, word), count in self.unary.iteritems():
      if sym not in rule_dic.keys():
        rule_dic[sym] = {}

#      if word in self.mapping.keys():
 #       print count, "UN-RULE", sym, self.mapping[word.lower()]
 #     else:
      print count, "UN-RULE", sym, word
      rule_dic[sym][word] = count

    for (sym, y1, y2), count in self.binary.iteritems():
      if sym not in rule_dic.keys():
        rule_dic[sym] = {}
      print count, "BI-RULE", sym, y1, y2
      rule_dic[sym][y1+" "+y2] = count

    ''' print rule dic with prob'''

    '''
    for key in rule_dic.keys():
      rule_dic[key] = Counter(rule_dic[key])
      total = sum(rule_dic[key].values())
      for value in rule_dic[key]:
        rule_dic[key][value] = float(rule_dic[key][value]) / total

    for key in rule_dic.keys():
      for value in rule_dic[key]:
        print key,"->",value, "#",rule_dic[key][value]

    return rule_dic  
    '''

  def count(self, tree):
    """
    Count the frequencies of non-terminals and rules in the tree.
    """
    if isinstance(tree, basestring): return

    # Count the non-terminal symbol. 
    symbol = tree[0]
    self.nonterm.setdefault(symbol, 0)
    self.nonterm[symbol] += 1
    
    if len(tree) == 3:
      # It is a binary rule.
      y1, y2 = (tree[1][0], tree[2][0])
      key = (symbol, y1, y2)
      self.binary.setdefault(key, 0)
      self.binary[(symbol, y1, y2)] += 1
      
      # Recursively count the children.
      self.count(tree[1])
      self.count(tree[2])
    elif len(tree) == 2:
      # It is a unary rule.
      y1 = tree[1]
      key = (symbol, y1)
      self.unary.setdefault(key, 0)
      self.unary[key] += 1

def train2json(line):
  json = ''
  word = []
  line = list(line)
#  line = line.strip()
  for ch in range(0,len(line)):
    if line[ch] == ")":
      if word != []:
        json = json + '"' + "".join(word) + '"'
      word = []
      if line[ch+1] != ")":
        if ch != len(line)-1:

          json = json + "],"
        else:
          json = json + "]"
      else:
        json = json + "]"
    elif line[ch] == "(":
      word = []
      flag = 1
      json = json + "["
    elif line[ch] == " ":
      if word != []:
        json = json + '"' + "".join(word) + '",'
      word = []
      json = json + line[ch]
    else:
      word.append(line[ch])
  return json

def main(parse_file):
  counter = Counts() 
  for l in open(parse_file):
    t = tree.Tree.fromstring(l.strip(), remove_empty_top_bracketing=True)
    collapsedTree = deepcopy(t)
    parentTree = deepcopy(collapsedTree)
    treetransforms.chomsky_normal_form(parentTree,horzMarkov=0,vertMarkov=1)
    l = parentTree.__str__()
    l = l.replace("\n","")
    l = re.sub(' +',' ',l)+"\n"

    k = train2json(l)
    k = k[:-1]
    t = json.loads(k)
#    print t
    counter.count(t)
  rule_dic = counter.show()
#  print rule_dic

def usage():
    sys.stderr.write("""
    Usage: python count_cfg_freq.py [tree_file]
        Print the counts of a corpus of trees.\n""")

if __name__ == "__main__":

  main(sys.argv[1])
  
