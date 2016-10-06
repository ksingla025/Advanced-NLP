#!/usr/bin/python

import sys,os,commands
from collections import Counter
from itertools import product
from itertools import groupby
from operator import itemgetter
from viterbi import viterbi as vt
import pickle

class EM_decipher(object):

	def __init__(self, cipher_data, english_data):

		self.english_data = open(english_data,'r').readlines()
		self.cipher_data = open(cipher_data,'r').readlines()
		
		self.states = set()
		for line in self.english_data:
			line = line.replace(" ","_")
			self.states = (self.states | set(line.strip()))
		self.states = list(self.states)

		self.end_state = '*end*'

		self.start_probability = self.get_start_prob()


		self.transition_probability = self.transition_probability()
 
 		self.emission_probability = self.init_emission_prob()

 #		print self.states
 #		print self.transition_probability
 #		print self.emission_probability

 #		print len(list(self.cipher_data[0].strip()))
 #		l = self.fwd_bkw(list(self.cipher_data[0].strip()),self.states,self.start_probability,self.transition_probability,self.emission_probability,self.end_state)
 #		print len(l)
 #		for line in self.example():
 #			print line

	def example(self):
		return self.fwd_bkw(list(self.cipher_data[0].strip()),self.states,self.start_probability,self.transition_probability,self.emission_probability,self.end_state)
 	
 	def em_learn(self, iter_num=40):

 		prob_je = {}
 		for iteration in range(iter_num):
 			print "======== Iteration :",iteration

 			posterior = self.fwd_bkw(list(self.cipher_data[0].strip()),self.states,self.start_probability,self.transition_probability,self.emission_probability,self.end_state)
 #			print posterior
 			cipher = list(self.cipher_data[0].strip())
 			print cipher
 			for i in range(0,len(cipher)):

 				
 				for key in posterior[i].keys():
 					if key not in prob_je.keys():
 						prob_je[key] = {}
 					if cipher[i] not in prob_je[key].keys():
 						prob_je[key][cipher[i]] = posterior[i][key]
 					else:
 						prob_je[key][cipher[i]] = prob_je[key][cipher[i]] + posterior[i][key]

 			total = 0.0
 			for key in prob_je.keys():
 				total = sum(prob_je[key].values())
 				prob_je[key]= {k: v / total for k, v in prob_je[key].iteritems()}
 				total = 0.0

 			self.emission_probability = prob_je

 		final = {}
 		for key in prob_je.keys():
 			for value in prob_je[key].keys():
 				if value not in final.keys():
 					final[value] = {}
 				if key not in final[value].keys():
 					final[value][key] = prob_je[key][value]
 				else:
 					final[value][key] = final[value][key] + prob_je[key][value]
 		
 		total = 0.0
 		for key in final.keys():
 			total = sum(final[key].values())
 			final[key]= {k: v / total for k, v in final[key].iteritems()}
 			total = 0.0

 		return final



	def get_start_prob(self):
		start = []
		for line in self.english_data:
			tokens = line.split()
			start.append(tokens[0][0])
		start_cnt = Counter(start)
		total = sum(start_cnt.values())
		for value in start_cnt:
			start_cnt[value] = float(start_cnt[value]) / total
		return start_cnt

	def transition_probability(self):
		bigram_list = []
		lines = ''
		for line in self.english_data:
			lines = lines + " " + line.strip()

		line = [lines[i:i+2] for i in range(len(lines)-1)]
		for k in line:
			if k[0] == " ":
				k = list(k)
				k[0] = "_"
				"".join(k)
			if k[1] == " ":
				k = list(k)
				k[1] = "_"
				"".join(k)
			if k[1] == "\n":
				k = list(k)
				k[1] = "*end*"

			bigram_list.append((k[0], k[1]))				

#		print bigram_list
		bigram_cnt = Counter(bigram_list)
		total = sum(bigram_cnt.values())
		for value in bigram_cnt:
			bigram_cnt[value] = float(bigram_cnt[value]) / total
		bigram_cnt = dict(bigram_cnt)
		transition = {}
		
		for key in bigram_cnt.keys():
			key_orig = key
			key = list(key)
			if key[0] not in transition.keys():
				transition[key[0]] = {}
			transition[key[0]][key[1]] = bigram_cnt[key_orig]

		for key in transition.keys():
			total = sum(transition[key].values())
			for value in transition[key].keys():
				transition[key][value] = float(transition[key][value]) / total

		for key in transition.keys():
			for state in self.states:

				if state not in transition[key].keys():
					transition[key][state] = 0.0000000
					transition[key]['*end*'] = float(1)/26
		return transition

	def init_emission_prob(self):
		cipher_observations = list(set(self.cipher_data[0].strip()))
		emission = {}
		for state in self.states:
			if state not in emission.keys():
				emission[state] = {}
			for i in cipher_observations:
				if state == '_':
					if i == " ":
						emission[state][i] = 1.0
					else:
						emission[state][i] = 0.0  
				else:
					if i == " ":
						emission[state][i] = 0.0
					else:	
						emission[state][i] = float(1)/len(cipher_observations) 
		return emission

	def fwd_bkw(self, x, states, a_0, a, e, end_st):
		L = len(x)
 
		fwd = []
		f_prev = {}
		# forward part of the algorithm
		for i, x_i in enumerate(x):
#			print i,x_i
			f_curr = {}
			for st in states:
#				print st
				if i == 0:
					# base case for the forward part
					prev_f_sum = a_0[st]
				else:
					prev_f_sum = sum(f_prev[k]*a[k][st] for k in states)
 
				f_curr[st] = e[st][x_i] * prev_f_sum
 
			fwd.append(f_curr)
			f_prev = f_curr

		p_fwd = sum(f_curr[k]*a[k][end_st] for k in states)
#		p_fwd = sum(f_curr[k]*a[k][end_st] for k in states)
 
		bkw = []
		b_prev = {}
		
		# backward part of the algorithm
		y = x
		y.extend(['None'])
		print "len",len(x)
		for i, x_i_plus in enumerate(reversed(y[1:])):
			b_curr = {}
			for st in states:
				if i == 0:
					# base case for backward part
					b_curr[st] = a[st][end_st]

				else:
					b_curr[st] = sum(a[st][l]*e[l][x_i_plus]*b_prev[l] for l in states)
#					print b_curr[st]
 
 #			print b_curr
			bkw.insert(0,b_curr)
			b_prev = b_curr
 
		p_bkw = sum(a_0[l] * e[l][x[0]] * b_curr[l] for l in states)
 
 #		print p_fwd
 #		print bkw
		# merging the two parts
		posterior = []
		for i in range(L):
	#		for st in states:
	#			print fwd[i][st]
	#			print bkw[i][st]
			posterior.append({st: fwd[i][st]*bkw[i][st]/p_fwd for st in states})
 
#		assert p_fwd == p_bkw
		return posterior
#		return fwd, bkw, posterior

if __name__ == "__main__":

	EM = EM_decipher("../data/cipher.data.toy","../data/english.data")
	prob_je = EM.em_learn()
	viterbi = vt(prob_je,"../data/english.data")
	viterbi.viterbi_search("MTBS SQTVTCEQZV TDSTNESM TX BZOZ WSQVEGS XTQJM TG TDS ITNMSGEGC ZCNEQJVTJNZV ZGW NSMTJNQS QTGWETETGM EG TDSTNESM")

#	print EM.states
#	print EM.start_probability 
#	print EM.transition_probability
#	print EM.emission_probability
	cipher = ["A" "B" "C"]
