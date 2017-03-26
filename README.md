# nlp-fact-extractor
The web is full of informative free-text resources, which might make some sense to a human being but not much to a computer, except might be as unstructured data or a bag of words. In this project, we are trying to implement Snowball system for the crucial task of extracting information/facts from massive free-text resources, such as Wikipedia and generating a database (semantic) of facts and information.

Semantic data allow machines to interact with worldly information without human interpretation. Semantic representation of data involves two entities and the relationship between them. For example, the sentence “Einstein was born in Germany.” would be represented as <Einstein, Germany> and the relationship would be "wasBornIn".

References:

[1] E. Agichtein and L. Gravano. Snowball: extracting relations from large plain-text collections. In ICDL, 2000.

[2] Information extraction from Wikipedia using pattern learning, Márton Miháltz & Péter Pázmány, Journal Acta Cybernetica archive Volume 19 Issue 4, January 2010 Issue-in-Progress, Pages 677-694.

[3] YAGO: A Core of Semantic Knowledge Unifying WordNet and Wikipedia, Fabian M. Suchanek, Gjergji Kasneci & Gerhard Weikum, Proceeding WWW '07 Proceedings of the 16th international conference on World Wide Web, Pages 697-706.

[4] Wikipedia data from: https://dumps.wikimedia.org/enwiki

[5] For cleaning wikipedia .xml data (to extract text): https://github.com/attardi/wikiextractor, http://medialab.di.unipi.it/wiki/Wikipedia_Extractor

[6] For tagging data we have used Stanford NER Tagger: https://nlp.stanford.edu/software/CRF-NER.html
