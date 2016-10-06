#!/usr/bin/python

import sys,os,commands
from collections import Counter
from itertools import product
from itertools import groupby
from operator import itemgetter
import pickle

from data2carmel import *
from viterbi import viterbi


class EM(object):

	def __init__(self,input_file):
		input_data = open(input_file,'r').readlines()
		input_data = [line for line in input_data if line.strip()]
		self.epron_data = input_data[::2]
		self.jpron_data = input_data[1::2]

		# get unique english sounds/words
		self.epron_words = []
		for line in self.epron_data:
			line = line.split()
			for word in line:
				if word.strip() not in self.epron_words:
					self.epron_words.append(word.strip())


		# get unique japanese sounds/words
		self.jpron_words = []
		for line in self.jpron_data:
			line = line.split()
			for word in line:
				if word.strip() not in self.jpron_words:
					self.jpron_words.append(word.strip())

		self.bigrams = find_bigrams(self.jpron_data)

#	def alignment_prob_initializer(self,alignments_pairs):
	def em_learn(self,iter_num = 5):

		prob_je = {}
		count_je = {}
		for iteration in range(0,iter_num):
				
			print "======== Iteration :",iteration
			print "\nSentences Processed "
#			for i in range(0,50):
			for i in range(0,len(self.epron_data)):
				
				print "\r%d" % i,
				
				alignment_prob = {}

				'''2a. enumerate all legal alignments a1...an'''
				legal_alignments = self.possible_alignments_pair(self.epron_data[i],self.jpron_data[i])

				# iteration = 0 then weights are initialized for all.
				'''2b. compute alignment probabilities P(a1)...P(an) as follows:'''
				if iteration == 0:
					for alignment in legal_alignments:
						
						alignment_prob[alignment] = 1.0/float(len(legal_alignments))

				else:
					for alignment in legal_alignments:
						orig_alignment = alignment
						alignment_prob[alignment] = 1
						alignment = alignment.split(";")
						for al in alignment:
							al = al.split(":")
							alignment_prob[orig_alignment] *=  prob_je[al[0]][al[1]]
						

				'''2c. collect fractional counts over all legal alignments'''
				for alignment in legal_alignments:
					
						align = alignment
						alignment = alignment.split(";")
						
						for al in alignment:
							
							al = al.split(":")
							if al[0] not in count_je.keys():
								count_je[al[0]] = {}
							if al[1] not in count_je[al[0]].keys():
								count_je[al[0]][al[1]] = 1*alignment_prob[align]
							else:
								
								count_je[al[0]][al[1]] = count_je[al[0]][al[1]] + 1*alignment_prob[align]


			''' 3. normalize sound-translation counts to yield P(J | e) estimates as follows:'''
			for ep in self.epron_words:
				total = 0
				for jp in count_je.keys():
					if ep in count_je[jp].keys():
						total += count_je[jp][ep]

				for jp in count_je.keys():
					if ep in count_je[jp].keys():
						if jp not in prob_je.keys():
							prob_je[jp] = {}
			

						prob_je[jp][ep] = count_je[jp][ep]/total
			
			


			''' 4. clear counts '''
			for jp in count_je.keys():
				for ep in count_je[jp].keys():
					count_je[jp][ep] = 0.0


		return prob_je


	def most_probable_alignment(self,prob_je,out_name):

		out_file = open(out_name,'w')

		for i in range(0,len(self.epron_data)):
			alignment_prob = {}
			legal_alignments = self.possible_alignments_pair(self.epron_data[i],self.jpron_data[i])

			for alignment in legal_alignments:
				orig_alignment = alignment
				alignment_prob[alignment] = 1
				alignment = alignment.split(";")
				for al in alignment:
					al = al.split(":")
					alignment_prob[orig_alignment] *=  prob_je[al[0]][al[1]]

			best_alignment =  max(alignment_prob.iteritems(), key=itemgetter(1))[0]
			best_alignment = best_alignment.split(";")
			
			epron = []
			jpron = []
			final_jpron = []
			alignment = []
			count = -1
			for i in best_alignment:
				count = count + 1
				token = i.split(":")
				epron.append(token[1])
				jpron.append(token[0])
		
			for i in range(0,len(jpron)):
				count = len(jpron[i].split())
				jpron[i] = jpron[i].split()
				for j in range(0,count):
					alignment.append(i+1)
					final_jpron.append(jpron[i][j])
			alignment = map(str, alignment)

			out_file.write(" ".join(epron)+"\n")
			out_file.write(" ".join(final_jpron)+"\n")
			out_file.write(" ".join(alignment)+"\n")
						
		out_file.close()



	def possible_alignments_pair(self,epron_word,jpron_word):

			

			sent_alignments = []
			epron = epron_word.split()
			epron = dict(enumerate(epron))

			jpron = jpron_word.split()
			jpron = dict(enumerate(jpron))

	#		print epron
	#		print jpron
			
			trips = [zip(jpron.keys(), p) for p in product(epron.keys(), repeat=len(jpron.keys()))]

			# possible patterns
			alignments = []
			for pattern in trips:

				en = []
				for align in pattern:
					align = list(align)
					if align[1] not in en:
						en.append(align[1])
				if en == epron.keys():
					alignments.append(pattern)
					sample = pattern


#					print pattern
			# generation check
#			correct_alignments = []
#			for sample in alignments:
					start_e = list(sample[0])[0]
					start_j = list(sample[0])[0]
					FLAG = 0

					for i in range(1,len(sample)):
						if int(list(sample[i])[1]) < int(start_e):
							FLAG = 1
							break
						elif int(list(sample[i])[0]) < int(start_j):
							FLAG = 1
							break
						else:
							start_e = list(sample[i])[1]
							start_j = list(sample[i])[0]

					if FLAG == 0:
						sample[0] = list(sample[0])
						s00 = 0
						sample[0][0] = jpron[sample[0][0]]
						sample[0][1] = epron[sample[0][1]]

						answer = [[sample[0][0],sample[0][1]]]

						for i in range(1,len(sample)):

							sample[i] = list(sample[i])
							sample[i][0] = jpron[sample[i][0]]
							sample[i][1] = epron[sample[i][1]]
#							sample[i] = zip(sample[i])

						sample2 = [list(group) for key, group in groupby(sample, itemgetter(1))]
						align_answer = {}
						sample3 = []
						for i in sample2:
							align_list = [item for sublist in i for item in sublist]
							if len(align_list) >= 4:
								tmp = align_list

								align_list[0] = " ".join(tmp[:-1][0::2])
								align_list[1] = tmp[-1]
								align_list = align_list[:2]
							
							sample3.append(align_list)
						sent_alignments.append(sample3)
			for al in range(0,len(sent_alignments)):
				ll = ''
				for k in range(0,len(sent_alignments[al])):
					sent_alignments[al][k] = ":".join(sent_alignments[al][k])
					if k == 0:
								
						ll = sent_alignments[al][k]
					else:
						ll = ll + ";" + sent_alignments[al][k]
				sent_alignments[al] = ll
			return  sent_alignments
			


def find_bigrams(input_list):
	bigram_list = []
	for line in input_list:
		line = line.split()
		line.insert(0,"*e*")
		for i in range(len(line)-1):
			bigram_list.append((line[i], line[i+1]))

	bigram_cnt = Counter(bigram_list)
	total = sum(bigram_cnt.values())
	for value in bigram_cnt:
			bigram_cnt[value] = float(bigram_cnt[value]) / total
	return bigram_cnt

def text2unigram(input_list):

	sent = []
	tag = []
	counter = 0
	for line in train_data:
		line = line.strip().split("/")
		if line[0] == ".":
			tag.append(line[1].strip())
#			out_data.write('"' + '" "'.join(sent) + '"\n')
#			out_data.write('"' + '" "'.join(tag) + '"\n')
		else:
			tag.append(line[1].strip())

	tag_cnt = Counter(tag)

	total = sum(tag_cnt.values())
	for value in tag_cnt:
			tag_cnt[value] = float(tag_cnt[value]) / total
	return tag_cnt

if __name__ == "__main__":

	
	out_folder = "output/"
	
	em = EM("data/epron-jpron-unsupervised.data")

	'''' Question 2 '''

	'''
	for i in range(0,5):
		k = em.possible_alignments_pair(em.epron_data[i], em.jpron_data[i])

		print "\n\n Pair "+str(i)+" possible alignments\n" 
		for best_alignment in k:
			best_alignment = best_alignment.split(";")
			epron = []
			jpron = []
			final_jpron = []
			alignment = []
			count = -1
			for i in best_alignment:
				count = count + 1
				token = i.split(":")
				epron.append(token[1])
				jpron.append(token[0])
		
			for i in range(0,len(jpron)):
				count = len(jpron[i].split())
				jpron[i] = jpron[i].split()
				for j in range(0,count):
					alignment.append(i+1)
					final_jpron.append(jpron[i][j])
			alignment = map(str, alignment)

			print " ".join(epron)
			print " ".join(final_jpron)
			print " ".join(alignment)
	'''

	''' train EM '''

#	em = EM("data/epron-jpron-unsupervised.data")

	commands.getstatusoutput("mkdir -p output")
	prob_je = em.em_learn(iter_num=20)
	with open(out_folder+'prob_je.pickle', 'wb') as handle:
		pickle.dump(prob_je, handle)

	''' align data '''
	em.most_probable_alignment(prob_je,out_folder+'epron_data.alignment')


#	print em.possible_alignments_pair(em.epron_data[0],em.jpron_data[0])
	

	''' creating fst using aligned data '''

#	dic = carmel2dic(out_folder+'epron_data.alignment')
#	print dic2fst(dic)


'''
def text2unigram(input_file):
	train_data = open(input_file,'r').readlines()


	sent = []
	tag = []
	counter = 0
	for line in train_data:
		line = line.strip().split("/")
		if line[0] == ".":
			tag.append(line[1].strip())
#			out_data.write('"' + '" "'.join(sent) + '"\n')
#			out_data.write('"' + '" "'.join(tag) + '"\n')
		else:
			tag.append(line[1].strip())

	tag_cnt = Counter(tag)

	total = sum(tag_cnt.values())
	for value in tag_cnt:
			tag_cnt[value] = float(tag_cnt[value]) / total
	return tag_cnt

def text2ngram(N,input_file):
	train_data = open(input_file,'r').readlines()
	NList = []
	tag = []                      # start with an empty list
	for line in train_data:
		line = line.strip().split("/")		
		if line[0] == ".":
			tag.append(line[1].strip())
			for i in range(len(tag)-N+1):
				NList.append(" ".join(tag[i:i+N]))
#			out_data.write('"' + '" "'.join(sent) + '"\n')
#			out_data.write('"' + '" "'.join(tag) + '"\n')
			tag = ["*e*"]
		else:
			tag.append(line[1].strip())	
	ngram_cnt = Counter(NList)
	total = sum(ngram_cnt.values())
	for value in ngram_cnt:
			ngram_cnt[value] = float(ngram_cnt[value]) / total
	return ngram_cnt

#	def target_grammer(self,input_file):
#		text2bigram = 


#	def EM_align(self):

'''
