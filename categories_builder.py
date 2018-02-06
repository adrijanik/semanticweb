#!/usr/bin/python

import csv
from string import Template
import rdflib as rdf
import os
from SPARQLWrapper import SPARQLWrapper, JSON

rdf_prefixes = """
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
"""

skos_concept = """
<$name> a skos:Concept;
skos:prefLabel"$label"@en
"""

broader = "skos:broader <$broader> "

narrower = "skos:narrower <$narrower> "


with open('categories.ttl', 'w') as out:
    out.write(rdf_prefixes)    
    with open('tags.txt') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        rdf_file = os.path.dirname(os.path.abspath(__file__)) + '/ted_talks_interface/ted_talks_interface/static_files/ted_talks_xml'
        query_category = os.path.dirname(os.path.abspath(__file__)) + '/ted_talks_interface/ted_talks_interface/static_files/get_broader_category.rq'
    
        g=rdf.Graph()
        g.load(rdf_file)
        concepts = {}
        for row in csvreader:
            name = row[0].strip().title()
            label = row[0].strip().lower()

            query = Template(open(query_category).read()).substitute(name=name)

            sparql = SPARQLWrapper("http://dbpedia.org/sparql")
            sparql.setReturnFormat(JSON)

            sparql.setQuery(Template("""prefix skos: <http://www.w3.org/2004/02/skos/core#>
                               PREFIX cat: <http://dbpedia.org/resource/Category:> 
                               select * where {
                                    cat:$name ?p ?broaderConcept .
                               }""").substitute(name=name))
            results = sparql.query().convert()
            if results:
                name = "http://dbpedia.org/resource/Category:" + name

            sparql = SPARQLWrapper("http://dbpedia.org/sparql")
            sparql.setReturnFormat(JSON)


            sparql.setQuery(query)
            results = sparql.query().convert()
            broads = set()
            narrows = set()
        #    print(results)
            for x in results['results']['bindings']:
                row = x['broaderConcept']['value'] 
                broads.add( Template(broader).substitute(broader=row))
                narrows.add(Template(narrower).substitute(narrower=name))
                br_name = row.split(':')[-1]
                if row  in concepts:
                    concepts[row][2] = concepts[row][2].union(narrows)
                else:
                    concepts[row] = [br_name, set(), narrows]
            narrows = set()
            if name in concepts:
                concepts[name][1] = concepts[name][1].union(broads)
                concepts[name][2] = concepts[name][2].union(narrows)
            else:
                concepts[name] = [label, broads, narrows]

        entries = []
        for item in concepts:
            print(item)
            b = '; \n'.join(concepts[item][1]) 
            n = '; \n'.join(concepts[item][2])
            c = ""
            if b != None and b != "" and n != None and n != "":
                c =  ';\n' + b + ';' + n + '.'
            if b != None and b != "" and n == None or n == "":
                c =  ';\n' + b + '.'
            if n != None and n != "" and b == None or b == "":
                c = ';\n' + n + '.'
            if b == None or b == "" and n == None or n == "":
                c = '.\n'



            entries.append(Template(skos_concept).substitute(name=item, label=concepts[item][0]).strip()+ c )

            
        out.write('\n'.join(entries).encode('utf8'))


