import requests
import json
from enum import Enum


class Deck:
    def __init__(self, name="", desc="", data_dict={}):
        if data_dict:
            self.id = data_dict["id"]
            self.name = data_dict["name"]
            self.desc = data_dict["desc"]
            self.usn = data_dict["usn"]
            self.mod = data_dict["mod"]
            self.collapsed = data_dict["collapsed"]
            self.time_today = data_dict["timeToday"]
            self.new_today = data_dict["newToday"]
            self.rev_today = data_dict["revToday"]
            self.lrn_today = data_dict["lrnToday"]
        else:
            self.name = name
            self.desc = desc

    def to_dict(self):
        data_dict = {"id": self.id, "name": self.name, "desc": self.desc, "usn": self.usn, "mod": self.mod,
                     "collapsed": self.collapsed, "timeToday": self.time_today,
                     "newToday": self.new_today, "revToday": self.rev_today,
                     "lrnToday": self.lrn_today}
        return data_dict


class RegularDeck(Deck):
    def __init__(self, name="", desc="", data_dict={}):
        super().__init__(name, desc, data_dict)
        if data_dict:
            self.extendRev = data_dict["extendRev"]
            self.extendNew = data_dict["extendNew"]
            self.conf = data_dict["conf"]
        else:
            self.extendRev = None
            self.extendNew = None
            self.conf = None

    def to_dict(self):
        data_dict = super().to_dict()
        data_dict["dyn"] = False
        data_dict["extendRev"] = self.extendRev
        data_dict["extendNew"] = self.extendNew
        data_dict["conf"] = self.conf


class DynamicDeck(Deck):
    def __init__(self, name="", desc="", terms="", data_dict={}):
        super().__init__(name, desc, data_dict)
        if data_dict:
            self.returning = data_dict["return"]
            self.resched = data_dict["resched"]
            self.delays = data_dict["delays"]
            self.separate = data_dict["separate"]
            self.terms = data_dict["terms"]
        else:
            self.returning = None
            self.resched = None
            self.delays = None
            self.separate = None
            self.terms = terms

    def to_dict(self):
        data_dict = super().to_dict()
        data_dict["dyn"] = True
        data_dict["resched"] = self.resched
        data_dict["delays"] = self.delays
        data_dict["separate"] = self.separate
        data_dict["terms"] = self.terms


class Note:
    def __init__(self, front="", back="", model="Basic", tags="", did="", data_dict={}):
        if not data_dict:
            self.id = 0
            self.front = front
            self.back = back
            self.model = model
            self.tags = tags
            self.did = did # Notes don't really have did, but its cards do
        else:
            self.from_dict(data_dict)

    def to_dict(self):
        data_dict = {"id": self.id,
                     "model": self.model,
                     "fields": {"Front": self.front,
                                "Back": self.back},
                     "tags": self.tags,
                     "did": self.did}
        return data_dict

    def from_dict(self, data_dict):
        self.id = data_dict["id"]
        self.front = data_dict["fields"]["Front"]
        self.back = data_dict["fields"]["Back"]
        self.model = data_dict["model"]
        self.tags = data_dict["tags"]


class AnkiRestClient:
    class Action(Enum):
        GET_NOTE = "get_note"
        ADD_NOTE = "add_note"
        FIND_NOTES = "find_notes"
        LIST_DECKS = "list_decks"
        SELECT_DECK = "select_deck"
        FIND_CARDS = "find_cards"

    def __init__(self, server_url, collection):
        self.collection = collection
        self.server_url = server_url

    def __json_headers(self):
        return {"Content-Type": "application/json",
                "Accept": "application/json"}

    def __complete_url(self, action, resource_id=""):
        complete_url = self.server_url + "/collection/" + self.collection + "/" + action.value
        if resource_id:
            complete_url += "/" + str(resource_id)
        return complete_url

    def __post(self, action, resource_id="", data_dict={}):
        try:
            response = requests.post(url=self.__complete_url(action, resource_id),
                                     data=json.dumps(data_dict),
                                     headers=self.__json_headers())
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as err:
            print(err, response.content)
            return err

    def get_note(self, nid):
        response = self.__post(action=self.Action.GET_NOTE,
                               resource_id=nid)
        json_dict = response.json()
        return Note(data_dict=json_dict)

    def add_note(self, note):
        response = self.__post(action=self.Action.ADD_NOTE,
                               data_dict=note.to_dict())
        return response

    def list_dynamic_decks(self):
        response = self.__post(action=self.Action.LIST_DECKS)
        decks = []
        for json_deck in response.json():
            if json_deck["dyn"]:
                decks.append(DynamicDeck(data_dict=json_deck))
        return decks

    def list_regular_decks(self):
        response = self.__post(self.Action.LIST_DECKS)
        decks = []
        for json_deck in response.json():
            if not json_deck["dyn"]:
                decks.append(RegularDeck(data_dict=json_deck))
        return decks

    def list_all_decks(self):
        response = self.__post(self.Action.LIST_DECKS)
        decks = []
        for json_deck in response.json():
            if json_deck["dyn"]:
                decks.append(DynamicDeck(json_dict=json_deck))
            else:
                decks.append(RegularDeck(data_dict=json_deck))
        return decks

    def list_all_cards(self):
        response = self.__post(action=self.Action.FIND_CARDS,
                               data_dict={"query": "", "preload": True})
        return response.json()

    def list_all_notes(self):
        response = self.__post(action=self.Action.FIND_NOTES,
                               data_dict={"query": "", "preload": True})
        nid_to_did_map = self.get_nid_to_did_map()
        notes = []
        for json_note in response.json():
            new_note = Note(data_dict=json_note)
            new_note.did = nid_to_did_map[new_note.id]
            notes.append(new_note)
        return notes

    # Useless?
    def select_deck(self, did):
        self.__post(self.Action.SELECT_DECK, {"deck": did})

    # Create filtered deck
    def create_dynamic_deck(self):
        print("Not implemented yet")

    # A note doesn't have a did, however, it seems like its cards
    # always have the same did, so it makes sense to map a note to
    # a specific did.
    def get_nid_to_did_map(self):
        nid_to_did_map = {}
        for card in self.list_all_cards():
            nid_to_did_map[card["nid"]] = card["did"]

        return nid_to_did_map



