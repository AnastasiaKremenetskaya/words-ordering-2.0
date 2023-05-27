import spacy
from rdflib import Graph, URIRef, Namespace, Literal, BNode
from rdflib.namespace import FOAF, RDF, RDFS
from collections import defaultdict

from categorize_adj import CategorizeADJ

NAMESPACE = "http://www.vstu.ru/poas/code#"


class ExtractADJ:

    def __init__(self):
        print("Initializing Spacy")
        self.nlp = spacy.load("en_core_web_sm")
        print("Initialized Spacy")

        # Определяем пространство имен
        self.ns = Namespace(NAMESPACE)
        # self.categorizer = CategorizeADJ()
        self.graph_nodes = dict()
        # self.node_id_by_names = defaultdict(list)

    def get_rdf(self, text):
        self.create_hypernyms_rules()
        doc = self.nlp(text)
        prev_pos_tag = None

        # Создаем RDF-модель
        g = Graph()

        for i, token in enumerate(doc):
            if i + 1 < len(doc):  # new
                next_token = doc[i + 1]
            else:
                next_token = None

            current_pos_tag = self.ns["item_"+str(i)]
            self.graph_nodes[token] = current_pos_tag
            # self.node_id_by_names[token.text].append(current_pos_tag.n3(g.namespace_manager))

            pos = token.pos_

            if pos in ['NOUN', 'PROPN']:
                if next_token is not None and (
                        next_token.tag_ == 'VBG' or
                        next_token.pos_ == 'NOUN' or
                        next_token.pos_ == 'PROPN' or
                        next_token.pos_ == 'ADJ'):
                    pos = 'ADJ'

            tag = pos
            if tag == "ADJ":
                # g.add((current_pos_tag, RDF.type, ns["hypernym"]))
                g.add((current_pos_tag, self.ns["hasHypernym"], self.ns["Material"]))
                #
                # tag = "ADJMaterial"  # tag + self.categorizer.infer(token.text)

            # задать классы
            g.add((current_pos_tag, RDF.type, self.ns[tag]))
            # g.add((current_pos_tag, RDF.type, ns["word"]))
            # g.add((current_pos_tag, RDF.type, ns["token"]))

            # g.add((current_pos_tag, ns["has"], ns["token"]))
            g.add((current_pos_tag, RDFS.label, Literal(token.text)))

            if prev_pos_tag is not None:
                g.add((prev_pos_tag, self.ns["tokenPrecedes"], current_pos_tag))

            prev_pos_tag = current_pos_tag

        # Добавить синтаксические связи и связь is_child
        for i, token in enumerate(doc):
            # g.add((self.graph_nodes[token], ns[token.dep_], self.graph_nodes[token.head]))

            for child in token.children:
                g.add((self.graph_nodes[child], self.ns["isChild"], self.graph_nodes[token]))

        # g.add((self.graph_nodes["The"], ns["#var..."], "X"))

        return g.serialize(format="ttl")

    def create_hypernyms_rules(self):
        hypernyms = [
            'Opinion',
            'Size',
            'PhysicalQuality',
            'Shape',
            'Age',
            'Colour',
            'Origin',
            'Material',
            'Type',
            'Purpose',
        ]

        # Создаем RDF-модель
        g = Graph()

        prev_hyp = self.ns[hypernyms[0]]
        g.add((prev_hyp, RDF.type, self.ns["hypernym"]))
        g.add((prev_hyp, RDFS.label, Literal(hypernyms[0])))
        for i in range(1, 9):
            hyp = self.ns[hypernyms[i]]
            g.add((hyp, RDF.type, self.ns["hypernym"]))
            g.add((hyp, RDFS.label, Literal(hypernyms[i])))
            g.add((prev_hyp, self.ns["hypernymPrecedes"], hyp))
            prev_hyp = hyp

        g.add((self.ns["DET"], RDFS.subClassOf, self.ns["word"]))
        g.add((self.ns["ADJ"], RDFS.subClassOf, self.ns["word"]))
        g.add((self.ns["NOUN"], RDFS.subClassOf, self.ns["word"]))

        print(g.serialize(format="ttl"))

if __name__ == "__main__":
    extractor = ExtractADJ()
    adjs = extractor.get_rdf("Japanese salt-cod sellers")
    print(adjs)
