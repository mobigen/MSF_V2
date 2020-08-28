# -*- coding:utf-8 -*-
import os
import lib.pretreatment.textmine.morph as morph
import lib.pretreatment.textmine.pykss as pykss
import lib.pretreatment.textmine.textrank as textrank
import lib.pretreatment.textmine.tokenizer as tokenizer


class textmine:

	def __init__(self, *args, **kwargs): 
		self.dic_path = str.format('%s/dict_system.tsv' % (os.path.abspath(os.path.dirname(__file__)))) 
		morph.dic_path = self.dic_path

	def get(self, content):
		try:
			sents = pykss.split_sentences(content)
			out_sents = []
			out_words = []
			out_sents = textrank.textrank_keysentences(sents, tokenize=tokenizer.morph_tokenize)
			out_words = textrank.textrank_keywords(sents, tokenize=tokenizer.morph_tokenize)
			return out_sents, out_words
		except Exception as ex:
			print("Except: %s" % str(ex))
