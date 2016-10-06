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
	PROB_MIN = 0.01
	mapping_dic = {} # it learns the mapping using alignment information
	
	data = open(input_file,'r').readlines()

	for i in range(0,len(data)):
		if i%3 == 2:
			input_seq = data[i-2].split()
			output_seq = data[i-1].split()
			align = data[i].split()
			mapping_local = {}
			for j in range(0,len(align)):
				if input_seq[int(align[j]) - 1] not in mapping_local.keys():
					mapping_local[input_seq[int(align[j]) - 1]] = output_seq[j]
				else:
					mapping_local[input_seq[int(align[j]) - 1]] = mapping_local[input_seq[int(align[j]) - 1]] + " " + output_seq[j]
			for key in mapping_local.keys():
				if key not in mapping_dic.keys():
					mapping_dic[key] = []
				mapping_dic[key].append(mapping_local[key])

	for key in mapping_dic.keys():
		mapping_dic[key] = Counter(mapping_dic[key])
		total = sum(mapping_dic[key].values())
		for value in mapping_dic[key]:
			mapping_dic[key][value] = float(mapping_dic[key][value]) / total
		mapping_dic[key] = dict((k, prob) for k, prob in mapping_dic[key].items() if prob >= PROB_MIN)
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