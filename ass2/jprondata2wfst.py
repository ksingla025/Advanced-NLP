#!/use/bin/python

import sys,re
from collections import Counter


data = open(sys.argv[1],'r').readlines()


#this function creates a fst for a dictionary

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




mapping_dic = {} # it learns the mapping using alignment information
PROB_MIN = 0.01

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
	mapping_dic[key] = dict((k, prob) for k, prob in mapping_dic[key].items() if prob >= PROB_MIN)

print dic2fst(mapping_dic)