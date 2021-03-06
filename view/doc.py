#!/usr/bin/env python
#    This file is part of le(n)x.

#    le(n)x is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    le(n)x is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with le(n)x.  If not, see <http://www.gnu.org/licenses/>.

# (C) 2009-2010 by Stefan Marsiske, <stefan.marsiske@gmail.com>

from lenx.view.db import Pippies, Frags, Docs, DocTexts, DocStems, DocTokens, fs

SLUGCHARS='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-'
def str_base(num, base=len(SLUGCHARS), numerals = SLUGCHARS):
    # src: http://code.activestate.com/recipes/65212/
    if base < 2 or base > len(numerals):
        raise ValueError("str_base: base must be between 2 and %i" % len(numerals))
    if num == 0:
        return '0'
    if num < 0:
        sign = '-'
        num = -num
    else:
        sign = ''
    result = ''
    while num:
        result = numerals[num % (base)] + result
        num //= base
    return sign + result

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def getStemmer(lang):
    if lang=="UNKNOWN": lang='en'
    lang=stopmap.lang_map[lang]
    if not stemmers[lang]:
        stemmers[lang]=hunspell.HunSpell("%s%s.dic" % (settings.DICT_PATH, lang), "%s%s.aff" % (settings.DICT_PATH, lang))
        #print 'new stemmer', lang, stemmers[lang]
    return stemmers[lang]

def Doc(*args, **kwargs):
    if 'docid' in kwargs:
        for (t,c,r) in DOCTYPES:
            if re.match(r,kwargs['docid']):
                return c(*args,**kwargs)
    if 'd' in kwargs:
        for (t,c,r) in DOCTYPES:
            if kwargs['d'].get('type','') == t or re.match(r,kwargs['d'].get('docid','')):
                return c(*args,**kwargs)
    if 'oid' in kwargs:
        dt=Docs.find_one({"_id": kwargs['oid']},['type'])['type']
        for (t,c,r) in DOCTYPES:
            if dt == t:
                return c(*args,**kwargs)
    return DOC(*args,**kwargs)

""" class representing a distinct document, does stemming, some minimal nlp, can be saved and loaded """
class DOC(object):
    computed_attrs = [ 'raw', 'body', 'text', 'tokens', 'stems', 'termcnt', 'tfidf', 'frags']
    fieldMap = {'raw': None, 'text': DocTexts, 'stems':  DocStems, 'tokens': DocTokens, }
    metafields = ['subject']

    def __init__(self,raw=None,docid=None,oid=None,d=None,owner=None):
        if oid:
            # get by mongo oid
            d=Docs.find_one({"_id": oid})
        elif docid:
            # get by docid
            d=Docs.find_one({"docid": docid})
        if d:
            # load the values
            self.__dict__.update(d)
        elif raw:
            # create a new document
            self.__dict__.update({
                'docid' : docid,
                'owner': unicode(owner),
                'pippies' : [],
                'pippiDocs' : [],
                'pippiDocsLen' : 0,
                'rawid' : None,
                'title': docid,
                })
            if not 'type' in self.__dict__:
                self.__dict__['type']='raw'
            if not 'metadata' in self.__dict__:
                self.__dict__['metadata']={}
            self.raw=raw
            self.__dict__['lang']=guessLanguage(" ".join(self.text))
            self.stems # for caching
            self.save()
        else:
            raise KeyError('empty docid')

    def __getattr__(self, name):
        # handle and cache calculated properties
        if name not in self.__dict__ or not self.__dict__[name]:
            if name == 'raw':
                return self._getraw() # cached on fs
            if name == 'text':
                self.__dict__['text'] = self._gettext() # cached in extfields
            if name == 'tokens':
                self.__dict__['tokens'] = self._gettokens() # cached in extfields
            if name == 'stems':
                self.__dict__['stems'] = self._getstems() # cached in extfields
            if name == 'termcnt':
                self.__dict__['termcnt']=self._getstemcount()
            if name == 'tfidf':
                self.__dict__['tfidf']=self._gettfidf()
            if name == 'title':
                self.__dict__['title']=self.docid
            if name == 'frags':
                return self._getfrags() # not cached at all
            if name == 'lang' and 'lang' not in self.__dict__.keys():
                return guessLanguage(" ".join(self._gettext()))
            if name == 'body':
                return self._getbody() # not cached
            if name in self.metafields:
                return ''
        if name in self.__dict__.keys():
            return self.__dict__[name]
        else:
            raise AttributeError, name

    def __setattr__(self, name, value):
        if name == 'raw':
            self._setraw(value) # cached on fs
        if name in self.__dict__.keys() or name in self.computed_attrs:
            self.__dict__[name]=value
        else: raise AttributeError, name

    def __unicode__(self):
        return self.docid

    def delete(self):
        for key, col in self.fieldMap.items():
            try:
                col.remove({'_id': self.__dict__["%sid" % key]})
            except:
                pass
        # TODO also remove pippies and other stuff cached after pippring
        Docs.remove({'_id': self.__dict__['_id']})

    def save(self):
        tmp=[(i,self.__dict__[i]) for i in self.fieldMap if i in self.__dict__]
        for i in tmp: del self.__dict__[i[0]]
        self.__dict__['_id']=Docs.save(self.__dict__)
        for (i,val) in tmp: self.__dict__[i]=val

    def _getraw(self):
        return fs.get(self.rawid).read()

    def _setraw(self, raw):
        f=fs.new_file()
        self.rawid=f._id
        if not self.docid:
            self.docid=str_base(int(str(hashlib.sha1(str(self.rawid)).hexdigest()),16))
        f.filename=self.docid
        f.write(raw)
        f.close()

    def _getbody(self):
        return unicode(str(BeautifulSoup(self.raw, convertEntities=BeautifulSoup.ALL_ENTITIES).body), 'utf8')

    def _gettext(self):
        res=self._getExtField('text')
        if res: return res
        soup = BeautifulSoup(self.raw,convertEntities=BeautifulSoup.ALL_ENTITIES)
        res = [unicode(x) for x in soup.body.findAll(text=True)]
        self._setExtField('text',res) # cache data
        return res

    def _gettokens(self):
        res=self._getExtField('tokens')
        if res: return res
        res = [token for frag in self.text if frag for token in nltk.tokenize.wordpunct_tokenize(unicode(frag))]
        self._setExtField('tokens',res) # cache data
        return res

    def _getstems(self):
        # start stemming
        stems= self._getExtField('stems') or []
        if stems:
            return tuple(stems)
        # lie about stems if we don't know how to
        if self.lang not in stopmap.stopmap.keys():
            return self.tokens

        stems=tuple([self._stem(w,self.lang) for w in self.tokens])
        # language aware stopwords removal
        stems=[x if x not in stopmap.stopmap[self.lang]and len(x)>1 else '' for x in stems]
        # result is a list of stems
        self._setExtField('stems',stems) # cache data
        return stems

    def _stem(self, word, lang):
        tmp=[x for x in word if x.isalpha()]
        if len(tmp)<len(word)*0.8:
             return ''
        s=getStemmer(lang).stem(word.encode('utf8'))

        if s:
            return s[0].decode('utf8')
        return ''

    def _getstemcount(self):
        termcnt={}
        for stem in self.stems:
            if not stem=='':
                termcnt[stem]=termcnt.get(stem,0)+1
        return termcnt

    def _gettfidf(self):
        return models.tfidf.get_doc_keywords(self)

    def _getfrags(self):
        return [models.Frag(frag=f) for f in self.getFrags(cutoff=1)]

    def __hash__(self):
        return hash(self._id)

    def __eq__(self,other):
        return self._id == other._id

    def getRelatedDocIds(self, cutoff=7):
        return set([doc
                    for pippi in Pippies.find({'len': { '$gte': int(cutoff)},
                                               'docs': self._id},
                                              ['docs'])
                    for doc in pippi['docs']
                    if doc != self._id])

    def getFrags(self, cutoff=7):
        return Frags.find({'l': { '$gte': int(cutoff)},
                           'doc': self._id,
                           }).sort([('l', pymongo.DESCENDING)])

    def addDoc(self,d):
        if not d._id in self.pippiDocs:
            self.pippiDocs.append(d._id)
            self.pippiDocsLen=len(self.pippiDocs)

    def _getExtField(self, field):
        if field+"id" in self.__dict__:
            res=self.fieldMap[field].find_one({'_id': self.__dict__[field+'id']})
            if res: return res['value']

    def _setExtField(self, field, data):
        self.__dict__[field+'id']=self.fieldMap[field].save({'value': data})

    def autoTags(self,l):
        return sorted(tagcloud.logTags('',tags=dict([(t,w*100000) for (t, w) in self.tfidf.items() if t not in stopwords.stopwords]),l=l),key=itemgetter('tag'))

from django.core.management import setup_environ
from lenx import settings
setup_environ(settings)
from lenx.brain import cache as Cache
CACHE=Cache.Cache(settings.CACHE_PATH)
import hunspell # get pyhunspell here: http://code.google.com/p/pyhunspell/
from lenx.brain import tagcloud, stopwords
from guess_language import guessLanguage
from lenx.brain import stopmap

stemmers=dict([(k, None) for k in stopmap.lang_map.values()])

import nltk.tokenize # get this from http://www.nltk.org/
from BeautifulSoup import BeautifulSoup # apt-get?
from operator import itemgetter
import pymongo, hashlib, re, htmlentitydefs
import models
from lenx.view.eurlex import CELEXRE, Eurlex

DOCTYPES=(('eurlex',Eurlex,CELEXRE),)
