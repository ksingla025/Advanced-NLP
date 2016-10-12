#!/usr/bin/python

import sys
from collections import OrderedDict
from collections import Counter
from math import log,exp


class viterbi(object):
	def __init__(self,word2tag,tag_file):
		
		self.word2tag = {}
		self.word2tag = word2tag

		self.text2unigram = text2ngram(1,tag_file)
#		print self.text2unigram
		self.text2bigram = text2ngram(2,tag_file)
#		print self.text2bigram
		self.bigram_matrix = self.bigram2matrix(self.text2bigram)

	def viterbi_search(self,text,format=0):
		
		# format = 1 means that input is a file
		# format = 0 means input is a string
		if format == 1:
			text = open(text,'r').readlines()
		else:
			text = [text]

		for input_text in text:		
			input_text = list(input_text)
			N = len(input_text)
			M = len(self.text2unigram.keys())
			tag_list = self.text2unigram.keys()
			tag_prob = self.text2unigram.values()

			Q = [[0 for i in range(M)] for j in range(N)]
			best_pred = [[0 for i in range(M)] for j in range(N)]
		
			''' initilization for starting word by choosing most probabble tag probabilities'''
			for j in range(0,M):
				Q[0][j] = tag_prob[j] + self.word2tag[input_text[0]][tag_list[j]]
		
			''' setting back parameters for others '''
			for i in range(1,N):
				for j in range(0,M):
					Q[i][j] = clog(0)
					best_pred[i][j] = clog(0)
					best_score = float("-infinity")
					for k in range(0,M):
						r = self.bigram_matrix[j][k] + self.word2tag[input_text[i]][tag_list[j]] + Q[i-1][k]
						if r > best_score:
							best_score = r
							best_pred[i][j] = k
							Q[i][j] = r

			''' best path tracer in reverse '''
			answer = []
			final_best = 0
			final_score = float("-infinity")
			for j in range(0,M):
				if Q[N-1][j] > final_score:
					final_score = Q[N-1][j]
					final_best = j
			answer.append(tag_list[final_best])
			current = final_best
			for i in range(N - 1,0,-1): 
				current = best_pred[i][current]
				answer.append(tag_list[current])

			''' reverse the list to get the answer '''
			print " ".join(answer[::-1]) # print it in reverse for the answer


		

	def bigram2matrix(self,bigram_dic):
		text2unigram = OrderedDict(self.text2unigram)
		bigram_matrix = [[0 for i in range(len(text2unigram.keys()))] for j in range(len(text2unigram.keys()))]
		for key in bigram_dic.keys():
			tags = key.split()
			index1 = text2unigram.keys().index(tags[0])
			index2 = text2unigram.keys().index(tags[1])
			bigram_matrix[index2][index1] = bigram_dic[key]
		return bigram_matrix

def text2ngram(N,input_file):
	NList = []
	data = open(input_file,'r').readlines()
	lines = ''
	for line in data:
		lines = lines + " " + line.strip()
	lines = lines.replace(" ","_")
	tag = list(lines)
	for i in range(len(tag)-N+1):
		NList.append(" ".join(tag[i:i+N]))

	ngram_cnt = Counter(NList)
	total = sum(ngram_cnt.values())
	for value in ngram_cnt:
			ngram_cnt[value] = clog(float(ngram_cnt[value]) / total)
	return ngram_cnt

def clog(a):
	if a == 0:
		return float("-infinity")
	elif a == 1:
		return 0.0
	else:
		return log(a)

def log_add(a,b):
	if a == float("-infinity"):
		return b
	if b == float("-infinity"):
		return a
	if a - b > 16:
		return a
	if a > b: 
		return a + log(1 + exp(b-a))
	if b - a > 16:
		return b
	if b > a:
		return b + log(1 + exp(a-b))