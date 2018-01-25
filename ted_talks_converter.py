#!/usr/bin/python

import csv
from string import Template
import re

rdf_prefixes = """
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix properties: <http://example.org/properties/> .
@prefix talks: <http://example.org/talks/> .
@prefix ma: <http://www.w3.org/ns/ma-ont.html> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
"""

row_template = """
<$url>
    properties:comments "$comment"^^xsd:integer ;
    ma:description \"\"\"$description\"\"\" ;
    ma:duration "$duration"^^xsd:integer ;
    properties:event "$event" ;
    properties:film_date "$film_date" ;
    properties:languages "$languages"^^xsd:integer  ;
    foaf:name "$main_speaker" ;
    properties:name "$name" ;
    properties:num_speaker "$num_speaker"^^xsd:integer ;
    properties:published_date "$published_date" ;
    properties:ratings "$ratings" ;
    properties:related_talks "$related_talks" ;
    properties:speaker_occupation "$speaker_occupation" ;
    dcterms:subject "$tags" ;
    ma:title "$title" ;
    properties:views "$views"^^xsd:integer  .
"""

# comments,description,duration,event,film_date,languages,main_speaker,name,num_speaker,published_date,ratings,related_talks,speaker_occupation,tags,title,url,views

with open('ted_talks.rdf', 'w') as out:
    out.write(rdf_prefixes)    
    with open('ted-talks/ted_main.csv') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)

        for row in csvreader:
            row_blueprint = Template(row_template)
            new_row = []
            for elem in row:
                new_row.append(elem.replace('"','').strip().decode('utf-8').encode('ascii',errors='ignore'))
            row = new_row
            record = row_blueprint.substitute(url=row[15], comment=row[0], description=row[1], duration=row[2],event=row[3],film_date=row[4],languages=row[5],main_speaker=row[6],name=row[7],num_speaker=row[8],published_date=row[9], ratings=row[10], related_talks=row[11], speaker_occupation=row[12],tags=row[13],title=row[14],views=row[16])
            out.write(record)



