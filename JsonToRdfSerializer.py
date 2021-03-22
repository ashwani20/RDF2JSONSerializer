from rdflib import *
import os
import json

class JsonToRdfSerializer():
    def parseSubject(self, subject, predicateObjectTuple):
        '''
        Iterates through each predicate and object tuple for a particular subject and maps them into a predicate
        Dictionary. If there are multiple objects for one predicate, then all the objects are grouped together as a list
        object.
        :param subject: subject in the RDF statement
        :param predicateObjectTuple: predicate and object tuple for a particular subject
        :return: a predicate Dictionary containing objects
        '''
        predicateDict = {}
        for eachEntry in predicateObjectTuple:
            predicate = self.rdfGraph.qname(eachEntry[0])
            object = eachEntry[1]
            resource = {}
            if isinstance(object, Literal):
                resource[predicate] = object
                if predicate in predicateDict:
                    if isinstance(predicateDict[predicate], str):
                        predicateDict[predicate] = [predicateDict[predicate]]
                    predicateDict[predicate].append(object)
                else:
                    predicateDict[predicate] = str(object)
            elif isinstance(object, URIRef):
                isURIRef = True
                resource["rdf:resource"] = str(object)
                if predicate not in predicateDict:
                    predicateDict[predicate] = resource
                else:
                    if isinstance(predicateDict[predicate], dict):
                        predicateDict[predicate] = [predicateDict[predicate]]
                    predicateDict[predicate].append(resource)
            elif isinstance(object, BNode):
                predicateDict[predicate] = self.parseSubject(object, self.rdfGraph.predicate_objects(object))
        return predicateDict

    def parseRDFData(self, file):
        '''
        accepts a file containing RDF data and transforms it into JSON format. Finally, returns the JSON data.
        :param file: file containing RDF data
        :return: transformed JSON data
        '''
        self.rdfGraph = Graph().parse(file, format='application/rdf+xml')
        self.jsonDict = {}

        namespaces = {}
        for eachNameSpace in self.rdfGraph.namespaces():
            namespaces[eachNameSpace[0]] = str(eachNameSpace[1])

        self.jsonDict['namespaces'] = namespaces

        for eachSubject in self.rdfGraph.subjects():
            if isinstance(eachSubject, BNode):
                continue
            self.jsonDict[eachSubject] = self.parseSubject(eachSubject, self.rdfGraph.predicate_objects(eachSubject))

        # first convert jsonDict to string using json.dumps() and then convert the Json string to
        # Json format
        jsonStr = json.dumps(self.jsonDict)
        return json.loads(jsonStr)


    def writeFile(self, jsonData, path, fileName):
        '''
        Writes JSON data into a file
        :param jsonData: JSON data
        :param path: path for the JSON data
        :param fileName: the name of the file
        :return:
        '''
        with open(path + fileName, 'w', encoding='utf-8') as file:
            file.write(str(jsonData))

    def readFile(self, filePath):
        '''
        Reads RDF data using the filePath and then calls parseRDFData method for converting RDF to JSON format and
        finally returns the transformed JSON data.
        :param filePath: the file path for the RDF data
        :return: transformed JSON data
        '''
        with open(filePath, "r", encoding='utf-8') as file:
            path, fileWithExt = os.path.split(filePath)
            fileName = fileWithExt.split(".")[0]
            jsonData = self.parseRDFData(file)
            newJsonFileName = fileName + '_converted.json'
            self.writeFile(jsonData, path, newJsonFileName)
            return jsonData


if __name__ == '__main__':
    obj = JsonToRdfSerializer()
    # jsonData = obj.readFile("amsterdammuseum_links.rdf")
    jsonData = obj.readFile("test1.rdf")
    print(jsonData)