import spacy
from rdflib import Graph, URIRef, Namespace, Literal, BNode
from rdflib.namespace import FOAF, RDF, RDFS

from categorize_adj import CategorizeADJ


class ExtractADJ:
    def __init__(self):
        print("Initializing Spacy")
        self.nlp = spacy.load("en_core_web_sm")
        print("Initialized Spacy")

        # Определяем пространство имен
        self.ns = Namespace("http://example.com/")
        self.categorizer = CategorizeADJ()
        self.graph_nodes = dict()

    def get_rdf(self, text):
        doc = self.nlp(text)
        prev_pos_tag = None

        # Создаем RDF-модель
        g = Graph()

        # Определяем пространство имен для частей речи и порядка слов
        ns = Namespace("http://example.com/")

        for i, token in enumerate(doc):
            if i + 1 < len(doc):  # new
                next_token = doc[i + 1]
            else:
                next_token = None

            current_pos_tag = BNode()
            self.graph_nodes[token] = current_pos_tag # учесть что могут быть одинаковые слова в предложении

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
                tag = tag + self.categorizer.infer(token.text)

            g.add((current_pos_tag, RDF.type, ns[tag]))
            g.add((current_pos_tag, RDFS.label, Literal(token.text)))

            if prev_pos_tag is not None:
                g.add((prev_pos_tag, ns.precedes, current_pos_tag))

            prev_pos_tag = current_pos_tag

        for i, token in enumerate(doc):
            g.add((self.graph_nodes[token], ns[token.dep_], self.graph_nodes[token.head]))

            for child in token.children:
                g.add((self.graph_nodes[child], ns.is_child, self.graph_nodes[token]))

        return g.serialize(format="xml")


if __name__ == "__main__":
    extractor = ExtractADJ()
    adjs = extractor.get_rdf("Young amazing English big-amazing-taste-cod sellers")
    print(adjs)
