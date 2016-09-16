#!/bin/python


import sys,commands



class FSA_creator(object):
	
	def __init__(self,infile):
		self.lines = []
		f = open(infile,'r')
		for line in f:
			line = line.strip()
			self.lines.append(line)

	def fsa_input_symbols(self):
		symbols = []
		for line in self.lines:
			tokens = line.split()
			for i in tokens:
				if i not in symbols:
					symbols.append(i)

		outsymb = open("fsa.in",'w')
		outsymb.write("-\t0\n")
		counter = 0
		for i in symbols:
			counter = counter + 1
			outsymb.write(str(i)+"\t"+str(counter)+"\n")
#		outsymb.write("_\t"+str(counter+1))
		outsymb.close()

	def fsa_text(self):
		outtext = open("fsa.text",'w')
		counter = 0
		temp = 0
		for line in self.lines:
			tokens = line.split()
			for i in range(0,len(tokens)):
				if i == 0:
					outtext.write("0\t"+str(temp+i+1)+"\t"+tokens[i]+"\n")
				elif i == len(tokens)-1:
					outtext.write(str(temp+i)+"\t12345678\t"+tokens[i]+"\n")
				else:
					outtext.write(str(temp+i)+"\t"+str(temp+i+1)+"\t"+tokens[i]+"\n")
			
#			outtext.write(str(temp+len(tokens))+"\t0\t_\n")
			outtext.write("12345678\n")
#			outtext.write(str(temp+len(tokens))+"\n")
			temp = temp + len(tokens)
			
	def compile_minimize(self):
		commands.getstatusoutput("fstcompile --acceptor -isymbols=fsa.in fsa.text > sent.fsa")
		commands.getstatusoutput("fstdeterminize sent.fsa | fstminimize > sent1.fsa")
		commands.getstatusoutput("fstprint --acceptor -isymbols=fsa.in sent1.fsa > dic.fsa")
		fsa = open("dic.fsa",'r')
		final_states = []
		transactions = []
		for line in fsa:
			if len(line.split()) == 1:
				if line not in final_states:
					final_states.append(line)
			else:
				transactions.append(line)
		print "12345678"
		for i in transactions:
			i = i.strip().split("\t")
			print '('+str(i[0])+' ('+str(i[1])+' "'+str(i[2])+'"))' 
		for i in final_states:
			print '('+str(i.strip())+' (12345678 *e*))'
		print '(12345678 (0 "_"))' 
k = FSA_creator(sys.argv[1])
#k.fsa_input_symbols()
#k.fsa_text()
k.compile_minimize()