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
    rating_title = "Choose rating"             
    rating_form = RatingsForm()
    talk_rating = {}
    name = ""
    tag_title = "Choose subject"             
    tag_form = TagsForm()
    talks_by_tag = {}
    talks_title = "Choose talk"             
    talks_form = TalksForm()
    talks_by_talk = {}


    if request.method == 'POST':
        
        if 'ratings_btn' in request.POST :
            print("True ratings")
            rating_form = RatingsForm(request.POST)
            if rating_form.is_valid():
                talk_rating, rating_title, name = get_highest_ratings(rating_form)
            else:
                rating_title = "Error"             
                rating_form = RatingsForm()
                talk_rating = {}
                name = ""

        if 'subject_btn' in request.POST :
            tag_form = TagsForm(request.POST)
            if tag_form.is_valid():
                talks_by_tag, tag_title = get_talks_by_subject(tag_form)
            else:
                tag_title = "Error"             
                tag_form = TagsForm()
                talks_by_tag = {}
        
        if 'related_btn' in request.POST :
            talks_form = TalksForm(request.POST)
            if talks_form.is_valid():
                talks_by_talk, talks_title = get_talks_by_talk(talks_form)
            else:
                talks_title = "Error"             
                talks_form = TalksForm()
                talks_by_talk = {}


    context = {"ratings": talk_rating, 'rating_form':rating_form, "rating_title":rating_title, "name":name, "talks_by_tag":talks_by_tag, 'tag_form':tag_form, "tag_title":tag_title, "talks_by_talk":talks_by_talk, 'talks_form':talks_form, "talks_title":talks_title}
    return render(request, 'index.html', context=context)


def get_highest_ratings(form):
    print("Highest rating")
    answer = form.cleaned_data.get('ratings') 

    owl_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_vocabulary.owl'
    rdf_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_talks_xml'
    query_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/most_funniest_talk_orderby.rq'
    query_talk_info = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/retrive_all_properties_of_talk.rq'

    g=rdf.Graph()
    g.load(rdf_file)
    query = open(query_file).read().replace('funny',answer)
    result =  g.query(query)
    props = {}
    name = ""
    for row in result:
        talk_query = Template(open(query_talk_info).read()).substitute(talk=row[0])
        properties =  g.query(talk_query)
        rats = []
        subjects = []
        talks = []
        for prop in properties:
    	    p = urlparse(prop[0]).path.split('/')[-1]
    	    if "ratings" in prop[0]:
    	        rats.append(prop)
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
                cmd ='curl http://model.dbpedia-spotlight.org/en/annotate --data-urlencode "text='+subs+'" --data "confidence=0.35" > out_subjects.txt'
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
                    cmd ='curl http://model.dbpedia-spotlight.org/en/annotate  --data-urlencode "text='+prop[1]+'"  --data "confidence=0.35" > out.txt'
                    out = os.system(cmd)
                    with open('out.txt') as f:
                        props[p]=f.read()
                    
            else:
                props[p]=prop[1]

    return  props, answer.upper(), name


def get_talks_by_talk(form):
    answer = form.cleaned_data.get('talks') 

    owl_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_vocabulary.owl'
    rdf_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_talks_xml'
    query_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/most_funniest_talk_orderby.rq'
    query_talk_info = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/retrive_all_properties_of_talk.rq'
    query_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/retrive_all_related_talks_simple.rq'
    query_url =  os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/get_url_of_a_talk.rq'


    g=rdf.Graph()
    g.load(rdf_file)
    
    query = open(query_file).read().replace('Doschoolskillcreativity',answer)
    query_url = open(query_url).read()
    print(query)
    result =  g.query(query)
    print(result)
    props = {}
    name = ""
    for i, row in enumerate(result):
        url = [r for r in g.query(Template(query_url).substitute(talk_name=row[0]))]
        print(row)
        if url:
            url = '<a href="' + str(url[0][0]) + '">' + str(url[0][0]) + '</a>'

        else:
            url = row[0]
        props[i]=url

    return props, answer.upper()


def get_talks_by_subject(form):
    answer = form.cleaned_data.get('tags') 

    owl_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_vocabulary.owl'
    rdf_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/ted_talks_xml'
    query_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/most_funniest_talk_orderby.rq'
    query_talk_info = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/retrive_all_properties_of_talk.rq'
    query_file = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/retrive_talks_by_tag_subject.rq'
    query_broader = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/retrive_talks_by_tag_broader.rq'
    query_narrower = os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/retrive_ted_talks_by_tags_narrow.rq'

    query_url =  os.path.dirname(os.path.abspath(__file__)) + '/../ted_talks_interface/static_files/get_url_of_a_talk.rq'


    g=rdf.Graph()
    g.load(rdf_file)
    query = open(query_file).read().replace('Law',answer)
    query_url = open(query_url).read()

    print(query)
    result =  g.query(query)
    print(result)
    props = {}
    name = ""
    for i, row in enumerate(result):
        url = [r for r in g.query(Template(query_url).substitute(talk_name=row[0]))]
        print(row)
        if url:
            url = '<a href="' + str(url[0][0]) + '">' + str(url[0][0]) + '</a>'

        else:
            url = row[0]
        props[i]=url

    query = open(query_broader).read().replace('Law',answer)
    
    print(query)
    result =  g.query(query)
    print(result)
    for k, row in enumerate(result):
        url = [r for r in g.query(Template(query_url).substitute(talk_name=row[0]))]
        print(row)
        if url:
            url = '<a href="' + str(url[0][0]) + '">' + str(url[0][0]) + '</a>'

        else:
            url = row[0]
        props[i + k]=url

    query = open(query_narrower).read().replace('Law',answer)
   
    print(query)
    result =  g.query(query)
    print(result)
    name = ""
    for m, row in enumerate(result):
        url = [r for r in g.query(Template(query_url).substitute(talk_name=row[0]))]
        print(row)
        if url:
            url = '<a href="' + str(url[0][0]) + '">' + str(url[0][0]) + '</a>'

        else:
            url = row[0]
        props[i + k + m]=url

    return props, answer.upper()

