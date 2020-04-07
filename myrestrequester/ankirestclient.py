import requests
import json

# TODO: Check exception handling

class noCollectionError(Exception):
    pass


class RestRequester:
    def __init__(self, url):
        self.url = url

    @classmethod
    def responseSuccess(cls, response):
        return response.status_code == 200

    def post(self, path, body = {}):
        headers = {"Content-type": "application/json"}
        req_url = "/".join([self.url, "/".join(path)])
        response = requests.post(req_url,
                                 data=json.dumps(body),
                                 headers=headers)
        response.raise_for_status()
        return response


class AnkiRestClient:
    def __init__(self, serverURL):
        self.config = {"serverURL": serverURL}
        # MOVE outside, should not be initialized inside here
        self.restRequester = RestRequester(serverURL)
        self.selectCollection("niknil")
        #self.selectedDeck = self.__selectFirstDeck()

    def __postRequest(self, path, body={}):
        if not self.config["collection"]:
            raise noCollectionError("A collection must be selected.")
        response = self.restRequester.post(path, body)
        return response

    # Create filtered deck
    def createDynamicDeck(self):
        print("Not implemented yet")

    def selectCollection(self, username):
        self.config["collection"] = username
        self.restRequester.url = "/".join([self.config["serverURL"], "collection", username])

    def getNote(self, id):
        response = self.__postRequest(["get_note", str(id)])
        jsonBody = response.json()
        return Note(jsonDict=jsonBody)

    def addNote(self, note):
        response = self.restRequester.post(["add_note"], note.jsonSerialize())
        return response

    def list_dynamic_decks(self):
        response = self.__postRequest(["list_decks"])
        decks = []
        for jsonDeck in response.json():
            if jsonDeck["dyn"]:
                decks.append(DynamicDeck(jsonDict=jsonDeck))
        return decks

    def list_regular_decks(self):
        response = self.__postRequest(["list_decks"])
        decks = []
        for jsonDeck in response.json():
            if not jsonDeck["dyn"]:
                decks.append(RegularDeck(jsonDict=jsonDeck))
        return decks

    def list_all_decks(self):
        response = self.__postRequest(["list_decks"])
        decks = []
        for jsonDeck in response.json():
            if jsonDeck["dyn"]:
                decks.append(DynamicDeck(jsonDict=jsonDeck))
            else:
                decks.append(RegularDeck(jsonDict=jsonDeck))
        return decks

    def listAllCards(self):
        jsonBody = {"query": "", "preload": True}
        response = self.__postRequest(["find_cards"], jsonBody)
        return response.json()

    def listAllNotes(self):
        jsonBody = {"query": "", "preload": True}
        response = self.__postRequest(["find_notes"], jsonBody)
        notes = []
        for jsonNote in response.json():
            notes.append(Note(jsonDict=jsonNote))
        return notes

    def selectDeck(self, did):
        jsonBody = {"deck": did}
        self.__postRequest(["select_deck"], jsonBody)

    def __selectFirstDeck(self):
        response = self.__postRequest(["list_decks"])
        jsonDecks = response.json()
        firstDeck = jsonDecks[0]["name"]
        self.selectDeck(firstDeck)
        return firstDeck





#    def update_note(id, datadict):
#        operation = "note/%d/update" % id
#        response = json_post_request(operation, datadict)
#        if response.status_code is 200:
#            return {}
#        else:
#            return {"Error": str(response.status_code)}
#

from typing import NamedTuple


class DeckStatusInfo(NamedTuple):
    timeToday: list
    newToday: list
    revToday: list
    lrnToday: list


class Deck:
    def __init__(self, name="", desc="", jsonDict={}):
        if jsonDict:
            self.id = jsonDict["id"]
            self.name = jsonDict["name"]
            self.desc = jsonDict["desc"]
            self.usn = jsonDict["usn"]  # Increase every time we do upload
            self.mod = jsonDict["mod"] # Time it was last modified?
            self.collapsed = jsonDict["collapsed"]   # Collapsing subdecks
            # Just skip MID if you don't need it.
            #if "mid" in jsonDict:
                #self.mid = jsonDict["mid"]  # Model id, not sure where this comes from or why it's needed
            #else:
                #print(jsonDict["name"] + " Doesn't have MID why?")
            self.deckStatusInfo = DeckStatusInfo(jsonDict["timeToday"],
                                                 jsonDict["newToday"],
                                                 jsonDict["revToday"],
                                                 jsonDict["lrnToday"])
        else:
            self.name = name
            self.desc = desc

    def jsonSerialize(self):
        jsonDict = {}
        jsonDict["id"] = self.id
        jsonDict["name"] = self.name
        jsonDict["desc"] = self.desc
        jsonDict["usn"] = self.usn
        jsonDict["mod"] = self.mod
        # jsonDict["mid"]  = self.mid # Which decks has mid?
        jsonDict["collapsed"] = self.collapsed
        jsonDict["timeToday"] = self.deckStatusInfo.timeToday
        jsonDict["newToday"] = self.deckStatusInfo.newToday
        jsonDict["revToday"] = self.deckStatusInfo.revToday
        jsonDict["lrnToday"] = self.deckStatusInfo.lrnToday
        return jsonDict


class RegularDeck(Deck):
    def __init__(self, name="", desc="", jsonDict={}):
        super().__init__(name, desc, jsonDict)
        if jsonDict:
            self.extendRev = jsonDict["extendRev"]
            self.extendNew = jsonDict["extendNew"]
            self.conf = jsonDict["conf"]
        else:
            self.extendRev = None
            self.extendNew = None
            self.conf = None

    def jsonSerialize(self):
        jsonDict = super().jsonSerialize()
        jsonDict["dyn"] = False
        jsonDict["extendRev"] = self.extendRev
        jsonDict["extendNew"] = self.extendNew
        jsonDict["conf"] = self.conf


class DynamicDeck(Deck):
    def __init__(self, name="", desc="", terms="", jsonDict={}):
        super().__init__(name, desc, jsonDict)
        if jsonDict:
            self.returning = jsonDict["return"]
            self.resched = jsonDict["resched"]
            self.delays = jsonDict["delays"]
            self.separate = jsonDict["separate"]
            self.terms = jsonDict["terms"]
        else:
            self.returning = None
            self.resched = None
            self.delays = None
            self.separate = None
            self.terms = terms

    def jsonSerialize(self):
        jsonDict = super().jsonSerialize()
        jsonDict["dyn"] = True
        jsonDict["resched"] = self.resched
        jsonDict["delays"] = self.delays
        jsonDict["separate"] = self.separate
        jsonDict["terms"] = self.terms


class Note:
    def __init__(self, front="", back="", model="Basic", tags="", did="", jsonDict={}):
        if not jsonDict:
            self.id = 0
            self.front = front
            self.back = back
            self.model = model
            self.tags = tags
            self.did = did # Notes don't really have did, but its cards have
        else:
            self.jsonDeserialize(jsonDict)

    def jsonSerialize(self):
        jsonDict = {"id": self.id,
                    "model": self.model,
                    "fields": {"Front": self.front,
                    "Back": self.back},
                    "tags": self.tags,
                    "did": self.did}
        return jsonDict

    def jsonDeserialize(self, jsonDict):
        fields = jsonDict["fields"]
        self.id = jsonDict["id"]
        self.front = jsonDict["fields"]["Front"]
        self.back = jsonDict["fields"]["Back"]
        self.model = jsonDict["model"] # TODO CHECK ALLOWED MODel
        self.tags = jsonDict["tags"]
        return self



