#!/usr/bin/python

import sys


def dic2fst(input_dic):
	fst = "0\n"
	count = 0
	for key in input_dic.keys():
				fst = fst + '(0 (0 "'+key+'" "'+input_dic[key]+'" 1.0))\n'
	return fst


input_file = open(sys.argv[1],'r').readlines()

plain = input_file[3].split(":")[1].strip()
cipher = input_file[4].split(":")[1].strip()
dic = {}
for i in range(0,len(plain)):
	dic[cipher[i]] = plain[i]

print dic2fst(dic)


