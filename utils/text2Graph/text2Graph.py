# External Libraries
from   pprint import pprint
import importlib
import json
import datetime
import time
import glob
import pandas as pd
import matplotlib.pyplot as plt
import re
import os, ssl
        
from operator import itemgetter as i
from functools import cmp_to_key
import time

def TicTocGenerator():
    # Generator that returns time differences
    ti = 0           # initial time
    tf = time.time() # final time
    while True:
        ti = tf
        tf = time.time()
        yield tf-ti # returns the time difference

TicToc = TicTocGenerator() # create an instance of the TicTocGen generator

# This will be the main function through which we define both tic() and toc()
def toc(tempBool=True):
    # Prints the time difference yielded by generator instance TicToc
    tempTimeInterval = next(TicToc)
    if tempBool:
        print( "Elapsed time: %f seconds.\n" %tempTimeInterval )

def tic():
    # Records a time in TicToc, marks the beginning of a time interval
    toc(False)


    
def cmp(x, y):
    return (x > y) - (x < y)

def multikeysort(items, columns):
    comparers = [
        ((i(col[1:].strip()), -1) if col.startswith('-') else (i(col.strip()), 1))
        for col in columns
    ]
    def comparer(left, right):
        comparer_iter = (
            cmp(fn(left), fn(right)) * mult
            for fn, mult in comparers
        )
        return next((result for result in comparer_iter if result), 0)
    return sorted(items, key=cmp_to_key(comparer))
    



if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
           
from   allennlp.predictors.predictor import Predictor
import allennlp_models.coref
import stanza
import spacy
import spacy_transformers
from   scispacy.abbreviation import AbbreviationDetector
from   scispacy.linking import EntityLinker
from   stanza.server import CoreNLPClient
import logging

from configuration.config import config
from utils.database.database import database           
db = database()  

class text2graph:
    
    def __init__(self): 
        logging.getLogger('allennlp.common.params').disabled = True 
        logging.getLogger('allennlp.nn.initializers').disabled = True 
        logging.getLogger('allennlp.modules.token_embedders.embedding').setLevel(logging.INFO) 
        logging.getLogger('urllib3.connectionpool').disabled = True 
        

        self.generateTables()
        self.text            = None
        self.entities        = None
        self.triples         = None
        self.coref_predictor = None
        self.entities_model  = None
        self.abbr_model      = None
        
        # INFORMATION EXTRACTION PARAMATERS
        self.client = None

    def generateTables(self):
        
        query = """CREATE TABLE IF NOT EXISTS `triples` (
                  `information_id`  bigint(20) unsigned NOT NULL AUTO_INCREMENT,
                  `pmid`            int(11)             NOT NULL     COMMENT 'The PubMed identification number.',
                  `pub_date`        date                DEFAULT NULL COMMENT 'The full date on which the issue of the journal was published.',
                  `subject`         varchar(200)        NOT NULL     COMMENT 'The subject of the sentence.',
                  `relation`        varchar(200)        NOT NULL     COMMENT 'The relationship between the subject and the objec.',
                  `object`          varchar(200)        NOT NULL     COMMENT 'The object of the sentence.',
                  `subject_hash`    varchar(32)         NOT NULL     COMMENT 'The pmid + object hash',
                  `relation_hash`   varchar(32)         NOT NULL     COMMENT 'The pmid + relation hash',
                  `object_hash`     varchar(32)         NOT NULL     COMMENT 'The pmid + subject hash',
                  `confidence`      int                 NOT NULL     COMMENT 'The confidence of the extraction',
                  `sentence_number` int                 NOT NULL     COMMENT 'The sentence that this showed up in.',
                  PRIMARY KEY (`information_id`),
                  UNIQUE KEY   `information_id`                 (`information_id`),
                  KEY          `information_pmid_index`         (`pmid`),
                  KEY          `information_pub_date_index`     (`pub_date`),
                  KEY          `information_subejcthash_index`  (`subject_hash`),
                  KEY          `information_realtionhash_index` (`relation_hash`),
                  KEY          `information_objecthash_index`   (`object_hash`),
                  KEY          `information_confidence_index`   (`confidence`),
                  KEY          `information_sentence_number`    (`sentence_number`),
                  FULLTEXT KEY `information_subject_index`      (`subject`),
                  FULLTEXT KEY `information_object_index`       (`relation`),
                  FULLTEXT KEY `information_relation_index`     (`object`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4"""
        
        db.query(query)


        query = """CREATE TABLE IF NOT EXISTS `concepts` (
                  `entity_id`            bigint(20) unsigned NOT NULL      AUTO_INCREMENT,
                  `triple_hash`          varchar(32)         NOT NULL      COMMENT 'Joins on triples.subject_key and triples.object_key',
                  `pmid`                 int(11)             NOT NULL      COMMENT 'The PubMed identification number.',
                  `pub_date`             date                DEFAULT NULL  COMMENT 'The full date on which the issue of the journal was published.',
                  `concept_type`         varchar(12)         NOT NULL      COMMENT 'e.g. subject, object, relation',
                  `concept_id`           varchar(20)         NOT NULL      COMMENT 'The Concept ID ',
                  `concept_name`         varchar(100)        NOT NULL      COMMENT 'The subject name.',
                  `sentence_number`      int                 NOT NULL      COMMENT 'The sentence that this showed up in.',
                  PRIMARY KEY (`entity_id`),
                  UNIQUE KEY `entity_id`              (`entity_id`),
                  KEY `entities_triplehash_index`     (`triple_hash`),
                  KEY `entities_pmid_class_index`     (`pmid`),
                  KEY `entities_sentence_number`      (`sentence_number`),
                  KEY `entities_pub_date_index`       (`pub_date`),
                  KEY `entities_pmiddate_index`       (`pub_date`,`pmid`),
                  KEY `entities_conceptid_index`      (`concept_id`),
                  KEY `entities_conceptname_index`    (`concept_name`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4"""
        db.query(query)

    #---------------------------------------------   
    # Coreferrence Resolution
    #---------------------------------------------
    def coreferenceResolution(self):
        
        if self.coref_predictor is None:
            self.coref_predictor = Predictor.from_path(config['NLP']['coreferenceResolution']['model'])
        
        prediction = self.coref_predictor.predict(document = self.text) 
        self.text  = self.coref_predictor.coref_resolved(self.text)
    
    #---------------------------------------------    
    # Lemmatize
    #---------------------------------------------
    def lemmatize(self):
        nlp       = stanza.Pipeline(lang='en', processors="tokenize, lemma", verbose = False)
        en_doc    = nlp(self.text)
        tokenized = []
        for i, sent in enumerate(en_doc.sentences):
            for j, token in enumerate(sent.words):
                tokenized.append(token.lemma)

        self.text = ' '.join(tokenized)
    
    #---------------------------------------------    
    # unAbbreviate     
    #---------------------------------------------
    def unAbbreviate(self):
        print('Initializing Abbreviation Model...')
        
        if self.abbr_model is None:
            self.abbr_model = spacy.load(config['NLP']['unAbbreviation']['model'])
            self.abbr_model.add_pipe("abbreviation_detector")
        
        doc = self.abbr_model(self.text)
        replace = {}
        for abrv in doc._.abbreviations:
            # Replace the first instance of the abbreviation 
            self.text = re.sub(f'\([ ]*{str(abrv)}[ ]*\)', '', self.text)
            
            #unabbreviate each instance
            replace[str(abrv)] = str(abrv._.long_form)
            self.text = self.text.replace(str(abrv),str(abrv._.long_form))
    

    def getEntities(self, text):
        
        # ENTITY EXTRACTION MODEL
        
        if self.entities_model is None:
            self.entities_model = {}
            for m, model in enumerate(config['NLP']['getEntities']['model']):
                print('Initializing Entity Extraction Model...')
                print('.... Please note: the entity extraction model only works for english documents.')
                print('.... documents containing non-english words may be skipped.')
                self.entities_model[model] = spacy.load(config['NLP']['getEntities']['model'][m])
                self.entities_model[model].add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "umls"})
        
        entities = {}
        # Get the set of entities using the model
        for model in config['NLP']['getEntities']['model']:
            try:
                bio_doc = self.entities_model[model](text)
            except:
                bio_doc = None

            #Find the link for each entity
            if bio_doc is not None:
                for entity in bio_doc.ents:
                    linker = self.entities_model[model].get_pipe("scispacy_linker")

                    for umls_ent in entity._.kb_ents:
                        if len(umls_ent) > 0:
                            _entity = {'alias'          : linker.kb.cui_to_entity[umls_ent[0]].aliases,
                                       'canonical_name' : linker.kb.cui_to_entity[umls_ent[0]].canonical_name,
                                       'concept_id'     : linker.kb.cui_to_entity[umls_ent[0]].concept_id,
                                       'definition'     : linker.kb.cui_to_entity[umls_ent[0]].definition,
                                       'types'          : linker.kb.cui_to_entity[umls_ent[0]].types
                                      }
                            entities[str(entity)] = _entity    
                        break
                #Store the entities information
        self.entities = entities
    
    #----------------------------------------------
    # Information Extraction
    #----------------------------------------------
    def informationExtraction(self,text):

        if self.client is None:
            print('--------------------------------------------')
            print('Initializing Information Extraction Model...')
            print('--------------------------------------------')
            self.client          = CoreNLPClient(timeout    = 150000,
                                                 be_quiet   = True,
                                                 properties = config['NLP']['informationExtraction']['properties'],
                                                 memory     = config['NLP']['informationExtraction']['memory'],
                                                 endpoint   = config['NLP']['informationExtraction']['endpoint'])
        
        triples  = []
        # Run the Information Extraction Client.
        document = self.client.annotate(text)
        for i,sentence in enumerate(document.sentence):
            for triple in sentence.openieTriple:
                
                triple = {'subject'    : triple.subject,
                          'relation'   : triple.relation,
                          'object'     : triple.object,
                          'confidence' : triple.confidence,
                          'sentence_number': i}
                triples.append(triple)
        self.triples = triples

    #----------------------------------------------
    # Process a set of documents
    #----------------------------------------------           
    def processDocuments(self, text_set, pmids, filter_results = True):
   
        ##########################################################################
        # Extracting Information
        ##########################################################################
        all_triples, all_entities  = [], {}
        for i, text in enumerate(text_set):
            if text is not None:
                
                # Do some basic cleansing of the text to remove items in the parentheses.
                
                self.text = re.sub(r'\([^)]*\)', '', text)
                
                #self.unAbbreviate()
                
                # Extract the entities
                self.getEntities(self.text)

                # Extract information triplets
                self.informationExtraction(self.text)

                # Asign the PMID to the triplet
                for triple in self.triples:
                    triple['pmid'] = str(pmids[i])
                all_triples += self.triples
                all_entities.update(self.entities)


        _entities = list(set(list(all_entities.keys()))) 
        _entities += ['COVID 19']
        
        #adding entity for COVID 19
        all_entities['COVID 19'] =  {'alias': ['Disease caused by 2019-nCoV', 'Disease caused by 2019 novel coronavirus (disorder)', 'Disease caused by 2019 novel coronavirus', 'Disease         caused by Wuhan coronavirus'], 'canonical_name': 'COVID-19', 'concept_id': 'C5203670', 'definition': None, 'types': ['T047']}
        
        #print(_entities)
        #print(all_entities)
        #print(all_triples)
        ##########################################################################
        # For each of the Triplets, we will assign matching entities
        ##########################################################################
        for i,triple in enumerate(all_triples):

            # Start by assuming there are no matching entities.
            in_object, in_subject = False, False
            triple['object_entity'], triple['subject_entity'], triple['relation_entity']  = {},{},{}
            triple['subject_count'], triple['object_count'],   triple['relation_count']   = 0,0,0

            triple['object_length']   = len(triple['object'])
            triple['subject_length']  = len(triple['subject'])
            triple['relation_length'] = len(triple['relation'])
            #Figure out the entities that appear in the subject and object portions.
            for entity in _entities:

                # Checking for entity in the object
                if str(entity) in triple['object']:
                    in_object  = True
                    triple['object_entity'][all_entities[entity]['concept_id']] = all_entities[entity]['canonical_name']
                    triple['object_count'] += 1
                    
                    
                # Checking for entity in the subject
                if str(entity) in triple['subject']:
                    in_subject = True
                    triple['subject_entity'][all_entities[entity]['concept_id']] = all_entities[entity]['canonical_name']
                    triple['subject_count'] += 1
                    

                # Checking for entity in the relation
                if str(entity) in triple['relation']:
                    in_relation = True
                    triple['relation_entity'][all_entities[entity]['concept_id']] = all_entities[entity]['canonical_name']
                    triple['relation_count'] += 1
                    
                    
            all_triples[i]['entity_match'] = False
            if in_subject and in_object:
                all_triples[i]['entity_match'] = True
        
        
        
        ##########################################################################
        # Apply Filtering Criteria at the end
        ##########################################################################
        if filter_results == True:
            all_triples = [x for x in all_triples if x.get('entity_match')]
    
            triples = multikeysort(all_triples,['sentence_number','-subject_count','-object_count','-relation_count','-relation','-subject','-object'])
            sentence_num = -1
            keep_triples = []
            for triple in triples:

                # The goal here is to trim down things that occur within a given sentence.
                if sentence_num != triple['sentence_number']:
                    sentence_num = triple['sentence_number']
                    completed = []

                subjects = set(triple['subject_entity'].keys())
                objects  = set(triple['object_entity'].keys())

                keep = True
                for pair in completed:
                    if subjects.issubset(pair['subjects']) and objects.issubset(pair['objects']):
                        keep = False
                        break

                if keep:
                    completed.append({'subjects' : subjects, 'objects' : objects})
                    keep_triples.append(triple)

            all_triples = keep_triples
        
        return all_triples