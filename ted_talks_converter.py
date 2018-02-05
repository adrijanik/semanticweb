#!/usr/bin/python

import csv
from string import Template

rdf_prefixes = """
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix properties: <http://example.org/properties/> .
@prefix ratings: <http://example.org/ratings/> .
@prefix talks: <http://example.org/talks/> .
@prefix ma: <http://www.w3.org/ns/ma-ont.html/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix talk: <http://www.example.org/talks.rdfs> .
"""

row_template = """
talks:$header a talk:Talk ;
    properties:comments "$comment"^^xsd:integer ;
    ma:description \"\"\"$description\"\"\" ;
    ma:duration "$duration"^^xsd:integer ;
    properties:event <#$event> ;
    properties:film_date "$film_date" ;
    properties:languages "$languages"^^xsd:integer  ;
    properties:speaker <#$main_speaker> ;
    properties:name "$name" ;
    properties:num_speaker "$num_speaker"^^xsd:integer ;
    properties:published_date "$published_date" ;
    properties:related_talks $related_talks ;
    dcterms:subject $tags ;
    ma:title "$title" ;
    properties:url "$url" ;
    properties:views "$views"^^xsd:integer  ;
"""

person_template = """
talks:$name a talk:Person ;
    foaf:name "$main_speaker" ;
    properties:speaker_occupation "$speaker_occupation" .
"""

event_template = """
talks:$name a talk:Event ;
    properties:name "$event" .
"""

tag_template = """
talks:$name a talk:Tag ;
    properties:name "$tag" .
"""


# comments,description,duration,event,film_date,languages,main_speaker,name,num_speaker,published_date,ratings,related_talks,speaker_occupation,tags,title,url,views

speakers = {}
events = set()
opinions = {}
tags = set()
with open('ted_talks.rdf', 'w') as out:
    out.write(rdf_prefixes)    
    with open('ted-talks/ted_main.csv') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)

        for row in csvreader:
            row_blueprint = Template(row_template)
            new_row = []
            for elem in row:
                new_row.append(elem.replace('"','').strip().decode('utf-8').encode('ascii',errors='ignore').replace('\\',''))
            row = new_row
            ratings = []
            opinion = ""
            vote = ""
            for t in row[10][2:-2].split('}, {'):
                for x in t.split(','):
                    if "name" in x.split(': ')[0]:
                        opinion = x.split(': ')[1].replace("'",'')
                    if "count" in x.split(': ')[0]:
                        vote = x.split(': ')[1].replace("'",'')
                ratings.append((opinion,vote))

            related_talks_titles = []
            for t in row[11][2:-2].split('}, {'):
                for x in t.split(','):
                    if "title" in x.split(': ')[0]:
                        related_talks_titles.append(x.split(': ')[1].replace("'",''))
            related_talks_template = "talks:$title"
            rel_string = ', '.join([Template(related_talks_template).substitute(title=filter(str.isalnum,t.replace(' ',''))) for t in related_talks_titles])
            tag_string = ', '.join([Template("talks:$name").substitute(name=t.strip().replace(' ','_')) for t in row[13][1:-1].replace("'",'').split(',')])
            record = row_blueprint.substitute(header=filter(str.isalnum,row[14].replace(' ','')), comment=row[0], description=row[1], duration=row[2],event=row[3].replace(' ','').strip().replace('>','').replace('<',''),film_date=row[4],languages=row[5],main_speaker=row[6].replace(' ','').strip(),name=row[7],num_speaker=row[8],published_date=row[9], related_talks=rel_string, tags=tag_string,title=row[14], url=row[15], views=row[16])
            rating_string = []
            for score in ratings:
                rating_string.append("ratings:" + score[0].lower().replace(' ','_') + ' ' + score[1])

            out.write(record + ';'.join(rating_string) + '.')
            speakers[filter(str.isalnum,row[6].replace(' ','').strip())] = (row[6], row[12])
            events.add(filter(str.isalnum,row[3]))
            tags.union(set(row[13][1:-1].split()))
    for tag in tags:
        t = Template(tag_template).substitute(name=tag, tag=tag)
        out.write(t)
    for speaker in speakers:
        person = Template(person_template).substitute(name=speaker, main_speaker=speakers[speaker][0], speaker_occupation=speakers[speaker][1])
        out.write(person)
    for event in events:
        e = Template(event_template).substitute(name=event.replace(' ','').strip().replace('>','').replace('<',''), event=event)
        out.write(e)




