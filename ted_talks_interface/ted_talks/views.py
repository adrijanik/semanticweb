from django.shortcuts import render
from django.views.generic import TemplateView
import rdflib as rdf
from rdflib import OWL, RDFS
import os
import rdfextras
import logging
from string import Template

logging.basicConfig()
rdfextras.registerplugins()

class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        owl_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_vocabulary.owl'
        rdf_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_talks_xml'
        query_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/most_funniest_talk_orderby.rq'
        query_talk_info = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/retrive_all_properties_of_talk.rq'


#        vocab = rdf.Namespace(open(owl_file).read())
        g=rdf.Graph()
        g.load(rdf_file)
        query = open(query_file).read()
#        nses = dict(owl=vocab)
        result =  g.query(query)
        props = {}
        for row in result:
            print("Most funniest talk id %s with %s votes" % row)
            talk_query = Template(open(query_talk_info).read()).substitute(talk=row[0])
            print(talk_query)
            properties =  g.query(talk_query)
            for prop in properties:
                print("%s -> %s" % prop)
                props[prop[0]]=prop[1]


#        for s,p,o in g:
#                print s,p,o
        context = {"talks": props}
        return render(request, 'index.html', context=context)
