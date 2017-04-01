import os
import bz2
import urllib
import time
import pickle

import nltk.tag.stanford as stag


def download_data(link, loc, delete_tmp=True):
    st = time.time()
    print "\nDownloading data from (this may take time): " + link
    if not os.path.exists(loc):
        os.makedirs(loc)

    file_path = loc + 'articles.xml.bz2'
    urllib.urlretrieve(link, file_path)
    print "Download Complete."
    print "Time Taken: %s ms" % str(time.time() - st)

    if not os.path.exists(file_path):
        return

    st = time.time()
    print '\nExtracting bz2 compressed file...'
    zipfile = bz2.BZ2File(file_path)  # open the file
    data = zipfile.read()  # get the decompressed data
    new_file_path = file_path[:-4]  # assuming the file_path ends with .bz2
    open(new_file_path, 'wb').write(data)  # write a uncompressed file
    zipfile.close()
    print "Time Taken: %s ms" % str(time.time() - st)

    if delete_tmp:
        os.remove(file_path)


def extract_data(loc, delete_tmp=True):
    st = time.time()
    print "\nExtracting necessary articles from wiki data..."

    f = open(loc + 'articles.xml', 'r')
    extracted_articles = bz2.BZ2File(loc + 'extracted_articles.xml.bz2', 'w')
    # TODO: Creating a fact file from infoboxes for testing
    fact_file = open('./data/facts', 'w')

    # Copying xml schema definitions to extracted file
    for line in f:
        if "<page>" not in line:
            extracted_articles.write(line)
        else:
            break

    # Copying only relevant articles from wiki data
    # to extracted data file (i.e. only company wiki pages)
    idx = 1
    f1 = open(loc + str(idx) + '.xml', 'w')
    flag = False

    for line in f:
        if "<page>" in line:
            f1 = open(loc + str(idx) + '.xml', 'w')
            f1.write(line)
            flag = False
        elif "Infobox company" in line:
            flag = True
            f1.write(line)
        elif "</page>" in line:
            if flag:
                f1.write(line)
                f1.close()

                f1 = open(loc + str(idx) + '.xml', 'r')
                extracted_articles.write(f1.read())
                f1.close()
                os.remove(loc + str(idx) + '.xml')

                if idx % 100 == 0:
                    print 'Extracted articles count: ' + str(idx)
                idx += 1
        else:
            f1.write(line)

    try:
        f1.close()
        if not flag:
            os.remove(loc + str(idx) + '.xml')
            idx -= 1
    except:
        pass

    extracted_articles.write('</mediawiki>')
    extracted_articles.close()
    f.close()
    print 'Extraction Complete.'
    print 'Total extracted articles: ' + str(idx - 1)
    print 'Time taken: %s ms' % str(time.time() - st)

    if delete_tmp:
        os.remove(loc + 'articles.xml')


def clean_data(loc, delete_tmp=True):
    st = time.time()
    print '\nCleaning articles to extract text only...'
    os.system('python ./lib/WikiExtractor.py -b 1000K -o ' + loc + ' ' + loc + 'extracted_articles.xml.bz2')
    print 'Time taken: %s ms' % str(time.time() - st)

    if delete_tmp:
        os.remove(loc + 'extracted_articles.xml.bz2')


def get_data(link, loc, delete_tmp=True):
    download_data(link, loc, delete_tmp)
    extract_data(loc, delete_tmp)
    clean_data(loc, delete_tmp)


def get_cleaned_and_tagged_data(link, delete_tmp=True):
    tmp_loc = './tmp/'
    data_loc = './data/'
    if not os.path.exists(tmp_loc):
        os.makedirs(tmp_loc)
    if not os.path.exists(data_loc):
        os.makedirs(data_loc)
        
    # get_data(link, tmp_loc)
    
    start = time.time()
    idx = 0
    print "\nTagging data using Stanford NER Tagger (this may take time)..."

    st = stag.StanfordNERTagger('./lib/english.all.3class.distsim.crf.ser.gz', './lib/stanford-ner.jar')
    for subdir, dirs, files in os.walk(tmp_loc):
        for file in files:
            r_file_path = os.path.join(subdir, file)
            f = open(r_file_path, 'r')

            w_file_path = data_loc + r_file_path[len(tmp_loc):]

            if not os.path.exists(os.path.dirname(w_file_path)):
                os.makedirs(os.path.dirname(w_file_path))

            td = open(w_file_path, 'w')
            for line in f:
                pickle.dump(st.tag(line.split()), td)
            td.close()
            idx += 1

            if idx % 5 == 0:
                print 'Tagging done for %s files' % str(idx)

    print 'Tagging Complete.'
    print 'Time taken: %s ms' % str(time.time() - start)


get_cleaned_and_tagged_data("https://dumps.wikimedia.org/enwiki/20170320/enwiki-20170320-pages-articles1.xml-p000000010p000030302.bz2")
