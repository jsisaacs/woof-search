#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import cgi
import os, random, math
import urllib.request

print('Content-Type: text/html\n')


form = cgi.FieldStorage()
query = form.getvalue("Query")
if query is None:
	query = "none"


def load_docs_mapping(file_mapping_path):
    try:
        docs = dict()
        with open(file_mapping_path, 'r', encoding="utf-8") as docs_dat:
            for line in docs_dat:
                line_split = line.split(', ')
                page = line_split[0]
                title = line_split[2]
                url = line_split[3].rstrip('\n')
                docs[page] = (title, url)
        return docs
    except:
        print('error parsing docs.dat')
        return None

def load_invindex_mapping(file_mapping_path):
    """
    takes the invindex.dat from assignment 2, converts it to a dictionary of
    dictionaries: key is the term, value is a dictionary where key is the
    document, value is the frequency per document and returns a tuple of the
    dict and the number of pages
    """
    try:
        invindex = dict()
        with open(file_mapping_path, 'r', encoding="utf-8") as invindex_dat:
            for line in invindex_dat:
                documents = dict()
                line_split = line.split(', ', 1)
                term = line_split[0]
                documents_and_frequency = line_split[1].split(' ')
                # this is because there is a trailing '\n' on each line
                documents_and_frequency.pop()
                invindex[term] = documents
                for doc_freq_pair in documents_and_frequency:
                    split = doc_freq_pair.split(':')
                    document = split[0]
                    frequency = int(split[1])
                    documents[document] = frequency
        pages = set()
        for page_frequencies in invindex.values():
            for page in page_frequencies.keys():
                pages.add(page)
        document_size = len(pages)
        return (invindex, document_size)
    except:
        print('error parsing invindex.dat')
        return None


def term_frequency(index, term, document):
    """
    takes an inverse index dictionary, term, and document to lookup frequency
    for and returns an integer or 0 if the term isn't found
    """
    try:
        page_frequencies = index[0][term][document]
        return page_frequencies / index[1]
    except:
        return 0


def inverse_document_frequency(index, term):
    """
    takes an index, term and document and returns the idf score
    """
    network_size = index[1]
    network_frequency = 0

    # for all documents in the network check and see how many have the term
    for i in range(network_size):
        document = str(i) + '.html'
        frequency = term_frequency(index, term, document)
        if frequency != 0:
            network_frequency += frequency
    idf = math.log10(network_size / (1 + abs(network_frequency)))
    return idf


def tf_idf(index, term, document):
    """
    takes an index, term, and document and returns the tf-idf score
    """
    tf = term_frequency(index, term, document)
    idf = inverse_document_frequency(index, term)
    tf_idf = tf * idf
    return tf_idf


def rank_pages(index, term):
    """
    takes an index and term, returns the list of pages ranked by tf-idf
    """
    page_ranking_dict = dict()
    network_size = index[1]
    network = list()
    for i in range(network_size):
        document = str(i) + '.html'
        network.append(document)
    for page in network:
        score = tf_idf(index, term, page)
        page_ranking_dict[page] = score
    ranked_network = sorted(page_ranking_dict, key=page_ranking_dict.get, reverse=True)
    network_score_tuple_list = list()
    for page in ranked_network:
        score = tf_idf(index, term, page)
        network_score_tuple_list.append((page, score))
    return network_score_tuple_list[:25]


def network_info(page, docs, ranked_network):
    """
    takes a page, returns a tuple (url, title, tf_idf score)
    """
    try:
        url = docs[page][1]
        title = docs[page][0]
        tf_idf = None
        for page_tuple in ranked_network:
            if page_tuple[0] == page:
                tf_idf = page_tuple[1]
        return (url, title, tf_idf)
    except:
        print('error getting network info')
     

docs = load_docs_mapping('docs.dat')
invindex_mapping = load_invindex_mapping('invindex.dat')

ranked_pages = rank_pages(invindex_mapping, query)

output = list()
for page in ranked_pages:
    output.append(network_info(page[0], docs, ranked_pages))


print('''
	<!doctype html>
	<html lang="en">
	  <head>
	    <meta charset="utf-8">
	    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
	    <title>Assignment 3: Search</title>
	  </head>
	  <body>
	    <div class="my-2 bg-light mx-2">
	      <div class="py-5 mx-5 text-center">
	      	<img src="icons8-pug-96.png" alt="Dog picture" height="60">
			<h1 class="pb-0">Search Results</h1>
			<a class="text-secondary" href="https://cgi.soic.indiana.edu/~jsisaacs/assignment3.html">back to search page</a>
			
	      
''')

index = 1

for page in output:
	url = str(page[0])
	title = str(page[1])[:-12]
	tfidf = format(page[2], '.2f')
	print('''
		   <div class="col-14
			 mx-auto my-4">
			  <div class="row justify-content-center">
			    <div class="col-6 pr-0">
			      <div class="text-justify"> 
			        <h5 class="text-dark">''' + title + '''</h5>
			        <a class="text-success" href="''' + url + '''">''' + url + '''</a>
			      </div>
			    </div>
			    <div class="mr-1 mt-2">
			      <h6 class="text-secondary">rank</h6>
			      <h6 class="text-dark">''' + str(index) + '''</h6>
				</div>
				<div class="ml-1 mt-2">
                  <h6 class="text-secondary">tf-idf</h6>
			      <h6 class="text-dark">''' + tfidf + '''</h6>
				</div>
			  </div>
			</div>
	''')
	index += 1

print('</div></div></body></html>')










