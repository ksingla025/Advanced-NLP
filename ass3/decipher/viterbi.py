#!/usr/bin/python

import sys
from collections import OrderedDict
from collections import Counter


class viterbi(object):
	def __init__(self,word2tag,tag_file):
		
		self.word2tag = {}
		self.word2tag = word2tag
		print self.word2tag
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

			print tag_prob
			print tag_list

			Q = [[0 for i in range(M)] for j in range(N)]
			best_pred = [[0 for i in range(M)] for j in range(N)]
		
			''' initilization for starting word by choosing most probabble tag probabilities'''
			for j in range(0,M):
				print tag_prob[j]
				print tag_list[j]
				print input_text[0]
				print self.word2tag[input_text[0]][tag_list[j]]
				Q[0][j] = tag_prob[j] * self.word2tag[input_text[0]][tag_list[j]]
		
			''' setting back parameters for others '''
			for i in range(1,N):
				for j in range(0,M):
					Q[i][j] = 0
					best_pred[i][j] = 0
					best_score = -999999999.0
					for k in range(0,M):
						r = self.bigram_matrix[j][k] * self.word2tag[input_text[i]][tag_list[j]] * Q[i-1][k]
						if r > best_score:
							best_score = r
							best_pred[i][j] = k
							Q[i][j] = r

			''' best path tracer in reverse '''
			answer = []
			final_best = 0
			final_score = -999999999.0
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
			ngram_cnt[value] = float(ngram_cnt[value]) / total
	return ngram_cnt
								
#vit = viterbi(sys.argv[1])
#print vit.word2tag
#vit.viterbi_search("how are you")