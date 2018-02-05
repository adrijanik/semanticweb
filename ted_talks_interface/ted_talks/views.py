from django.shortcuts import render
from django.views.generic import TemplateView
import rdflib as rdf
from rdflib import OWL, RDFS
import os
import rdfextras
import logging
from string import Template
from urlparse import urlparse
import datetime
from .forms import RatingsForm, TagsForm, TalksForm
import pygal

logging.basicConfig()
rdfextras.registerplugins()


def homepage(request):

    if request.method == 'POST':
        form = RatingsForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data.get('ratings') 

            owl_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_vocabulary.owl'
            rdf_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_talks_xml'
            query_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/most_funniest_talk_orderby.rq'
            query_talk_info = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/retrive_all_properties_of_talk.rq'
    
    
    #        vocab = rdf.Namespace(open(owl_file).read())
            g=rdf.Graph()
            g.load(rdf_file)
            query = open(query_file).read().replace('funny',answer)
    #        nses = dict(owl=vocab)
            result =  g.query(query)
            props = {}
            name = ""
            for row in result:
                #print("Most funniest talk id %s with %s votes" % row)
                talk_query = Template(open(query_talk_info).read()).substitute(talk=row[0])
                #print(talk_query)
                properties =  g.query(talk_query)
                rats = []
                subjects = []
                talks = []
                for prop in properties:
    		#    print("%s -> %s" % prop)
            	    p = urlparse(prop[0]).path.split('/')[-1]
            	    if "ratings" in prop[0]:
            	        rats.append(prop)
#            	        props["ratings"] = "<table>" + "".join(["<tr><td>{}: {}</td></tr>".format(urlparse(k[0]).path.split('/')[-1],k[1]) for k in sorted(rats, key=lambda x: x[1], reverse=True)])  + "</table>"
                        line_chart = pygal.Bar()
                        line_chart.title = 'Ratings'
                        for r in rats:
                            line_chart.add(urlparse(r[0]).path.split('/')[-1], int(r[1]))
                        line_chart.render_to_file('ratings.svg')
                        props["ratings"] = open('ratings.svg').read()

            	    elif "url" in p:
                   	    props[p] = '<a href="' + prop[1] + '">' + prop[1] + '</a>'
                    elif "subject" in p:
                        subjects.append(urlparse(prop[1]).path.split('/')[-1])
                        subs = ', '.join(subjects)
                        print(subs)
                        cmd ='curl http://model.dbpedia-spotlight.org/en/annotate  \
--data-urlencode "text='+subs+'" \
--data "confidence=0.35" > out_subjects.txt'
                        out = os.system(cmd)
                        with open('out_subjects.txt') as f:
                            props[p]=f.read()

                    elif "related_talks" in p:
                        talks.append(urlparse(prop[1]).path.split('/')[-1])
                        props[p] = ', '.join(talks)
                    elif "speaker" in p:
                        props[p] = prop[1].split("#")[-1]
                    elif "event" in p:
                        props[p] = prop[1].split("#")[-1]
                    elif "talks.rdfsTalk" in prop[1]:
                        continue
                    elif "date" in p:
                        props[p]=datetime.datetime.fromtimestamp(
                                        int(prop[1])
                                            ).strftime('%Y-%m-%d %H:%M:%S')
                    elif "title" in p:
                        name = prop[1]
                        props[p]=prop[1]
                    elif "description" in p:
                        if prop[1] != "":                   
                            cmd ='curl http://model.dbpedia-spotlight.org/en/annotate  \
  --data-urlencode "text='+prop[1]+'" \
  --data "confidence=0.35" > out.txt'
                            out = os.system(cmd)
                            with open('out.txt') as f:
                                props[p]=f.read()
                            
                    else:
                        props[p]=prop[1]
        else:
           title = "Error"             
           form = RatingsForm()
           props = {}
           answer = title
           name = ""
    else:
       title = "Choose rating"             
       form = RatingsForm()
       props = {}
       answer = title
       name = ""

    
    #        for s,p,o in g:
    #                print s,p,o
    context = {"talks": props, "title":answer.upper(), "form":form, "name":name}
    return render(request, 'index.html', context=context)

def related_talks(request):

    if request.method == 'POST':
        form = TalksForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data.get('talks') 

            owl_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_vocabulary.owl'
            rdf_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_talks_xml'
            query_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/most_funniest_talk_orderby.rq'
            query_talk_info = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/retrive_all_properties_of_talk.rq'
            query_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/retrive_all_related_talks_simple.rq'
   
    
    #        vocab = rdf.Namespace(open(owl_file).read())
            g=rdf.Graph()
            g.load(rdf_file)
            
            query = open(query_file).read().replace('Doschoolskillcreativity',answer)
            print(query)
    #        nses = dict(owl=vocab)
            result =  g.query(query)
            print(result)
            props = {}
            name = ""
            for i, row in enumerate(result):
                print(row)
                props[i]=row[0]
        else:
           title = "Error"             
           form = TalksForm()
           props = {}
           answer = title
           name = ""
    else:
       title = "Choose rating"             
       form = TalksForm()
       props = {}
       answer = title
       name = ""

    
    #        for s,p,o in g:
    #                print s,p,o
    context = {"talks": props, "title":answer.upper(), "form":form, "name":name}
    return render(request, 'index.html', context=context)


def tag_related_talks(request):

    if request.method == 'POST':
        form = TagsForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data.get('tags') 

            owl_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_vocabulary.owl'
            rdf_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_talks_xml'
            query_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/most_funniest_talk_orderby.rq'
            query_talk_info = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/retrive_all_properties_of_talk.rq'
            query_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/retrive_talks_by_tag_simple.rq'
   
    
    #        vocab = rdf.Namespace(open(owl_file).read())
            g=rdf.Graph()
            g.load(rdf_file)
            query = open(query_file).read().replace('children',answer)
            print(query)
    #        nses = dict(owl=vocab)
            result =  g.query(query)
            print(result)
            props = {}
            name = ""
            for i, row in enumerate(result):
                print(row)
                props[i]=row[0]
        else:
           title = "Error"             
           form = TagsForm()
           props = {}
           answer = title
           name = ""
    else:
       title = "Choose rating"             
       form = TagsForm()
       props = {}
       answer = title
       name = ""

    
    #        for s,p,o in g:
    #                print s,p,o
    context = {"talks": props, "title":answer.upper(), "form":form, "name":name}
    return render(request, 'index.html', context=context)
