#!/usr/bin/python

'''convers format to carmel text format'''

import sys
from collections import Counter

def text2carmel(input_file,out_file):	
	train_data = open(input_file,'r').readlines()
	out_data = open(out_file,'w')
	sent = []
	tag = []
	for line in train_data:
		line = line.split("/")
		if line[0] == ".":
			sent.append(line[0].lower())
			tag.append(line[1].lower().strip())
			out_data.write('"' + '" "'.join(sent) + '"\n')
			out_data.write('"' + '" "'.join(tag) + '"\n')
			sent = []
			tag = []
		else:
			sent.append(line[0])
			tag.append(line[1].strip())

def carmel2dic(input_file):
	mapping_dic = {} # it learns the mapping using alignment information
	data = open(input_file,'r').readlines()
	for i in range(0,len(data)):
		if i%2 == 1:
			input_seq = data[i-1].split()
			output_seq = data[i].split()
			dictionary = dict(zip(input_seq, output_seq))		
			for key in dictionary.keys():
				if key not in mapping_dic.keys():
					mapping_dic[key] = []
				mapping_dic[key].append(dictionary[key])

	'''
	1. put a counter on the values for eaching mapping symbol
	2. convert the counter into probability
	3. removes the ones which have probability less than PROB_MIN
	'''
	for key in mapping_dic.keys():
		mapping_dic[key] = Counter(mapping_dic[key])
		total = sum(mapping_dic[key].values())
		for value in mapping_dic[key]:
			mapping_dic[key][value] = float(mapping_dic[key][value]) / total

	return mapping_dic			

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
			tag.append("*e*")
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

def bidic2fsa(input_dic):
	fst = "56\n"
	count = 0
	tag_cnt = 0
	tag_dic = {}
	for key in input_dic.keys():
		if key.split()[0] == '*e*':
			tag_cnt = tag_cnt + 1
			tag_dic[tag_cnt] = key.split()[1]
			fst = fst + '(0 ('+str(tag_cnt)+' "'+key.split()[1]+'" '+str(input_dic[key])+'))\n'
	
	for key in input_dic.keys():
		if key.split()[1] == 		
		if key.split()[1] == '*e*':

	return fst

def dic2fsa(input_dic):
	fst = "0\n"
	count = 0
	for key in input_dic.keys():
		if len(key.split()) == 1:
			fst = fst + '(0 (0 "'+key+'" '+str(input_dic[key])+'))\n'
		if len(key.split()) == 2:
			count = count + 1
			fst = fst + '(0 ('+str(count)+' "'+key.split()[0]+'" ))\n'
			fst = fst + '('+str(count)+' (0 "'+key.split()[1]+'" '+str(input_dic[key])+'))\n'			
	return fst

def dic2fst(input_dic):
	fst = "0\n"
	count = 0
	for key in input_dic.keys():
		for value in input_dic[key].keys():
			if len(value.split()) == 1:
				fst = fst + '(0 (0 '+key+' '+value+' '+str(input_dic[key][value])+'))\n'
			
			if len(value.split()) == 2:
				count = count + 1
				fst = fst + '(0 ('+str(count)+' '+key+' '+value.split()[0]+' '+str(input_dic[key][value])+'))\n'
				fst = fst + '('+str(count)+' (0 *e* '+value.split()[1]+' '+str(input_dic[key][value])+'))\n'
			if len(value.split()) == 3:
				count = count + 1
				fst = fst + '(0 ('+str(count)+' '+key+' '+value.split()[0]+' '+str(input_dic[key][value])+'))\n'
				count = count + 1
				fst = fst + '('+str(count-1)+' ('+str(count)+' *e* '+value.split()[1]+' '+str(input_dic[key][value])+'))\n'
				fst = fst + '('+str(count)+' (0 *e* '+value.split()[2]+' '+str(input_dic[key][value])+'))\n'
			if len(value.split()) == 4:
				count = count + 1
				fst = fst + '(0 ('+str(count)+' '+key+' '+value.split()[0]+' '+str(input_dic[key][value])+'))\n'
				count = count + 1
				fst = fst + '('+str(count-1)+' ('+str(count)+' *e* '+value.split()[1]+' '+str(input_dic[key][value])+'))\n'
				count = count + 1
				fst = fst + '('+str(count-1)+' ('+str(count)+' *e* '+value.split()[2]+' '+str(input_dic[key][value])+'))\n'
				fst = fst + '('+str(count)+' (0 *e* '+value.split()[3]+' '+str(input_dic[key][value])+'))\n'

	return fst

''' generate tag unigram '''
#uni_tag = text2unigram(sys.argv[1])
#print dic2fsa(uni_tag)

''' generate tag bigram '''
#bi_tag = text2ngram(2,sys.argv[1])
#print dic2fsa(bi_tag)


#text2carmel(sys.argv[1],"tmp")
#dictionary = carmel2dic("tmp","oo")
#print dic2fst(dictionary)