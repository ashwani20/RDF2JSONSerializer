from rdflib import *
import json

class JsonToRdfSerializer():
    def parseSubject(self, subject, predicateObjectTuple, tempDict):
        tempDict = {}
        for eachEntry in predicateObjectTuple:
            predicate = self.rdfGraph.qname(eachEntry[0])
            object = eachEntry[1]
            resource = {}
            if isinstance(object, Literal):
                resource[predicate] = object
                if predicate in tempDict:
                    if isinstance(tempDict[predicate], str):
                        tempDict[predicate] = [tempDict[predicate]]
                    tempDict[predicate].append(resource)
                else:
                    tempDict[predicate] = str(object)
            elif isinstance(object, URIRef):
                isURIRef = True
                resource["rdf:resource"] = str(object)
                if predicate not in tempDict:
                    tempDict[predicate] = resource
                else:
                    if isinstance(tempDict[predicate], dict):
                        tempDict[predicate] = [tempDict[predicate]]
                    tempDict[predicate].append(resource)

        return tempDict

    def parseRDFData(self, file):
        self.rdfGraph = Graph().parse(file, format='application/rdf+xml')
        self.jsonDict = {}

        namespaces = {}
        for eachNameSpace in self.rdfGraph.namespaces():
            namespaces[eachNameSpace[0]] = str(eachNameSpace[1])

        self.jsonDict['namespaces'] = namespaces

        for eachSubject in self.rdfGraph.subjects():
            tempDict = {}
            self.jsonDict[eachSubject] = self.parseSubject(eachSubject, self.rdfGraph.predicate_objects(eachSubject),
                                                           tempDict)

        # first convert jsonDict to string using json.dumps() and then convert the Json string to
        # Json format
        jsonStr = json.dumps(self.jsonDict)
        return json.loads(jsonStr)

    def readFile(self, filePath):
        with open(filePath, "r", encoding='utf-8') as file:
            return self.parseRDFData(file)



if __name__ == '__main__':
    obj = JsonToRdfSerializer()
    jsonData = obj.readFile("amsterdammuseum_links.rdf")
    print(jsonData)
    # print(jsonData['namespaces'])