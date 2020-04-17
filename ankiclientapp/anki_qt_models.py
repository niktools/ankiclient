from PySide2.QtCore import QSortFilterProxyModel, QAbstractListModel, Qt, Slot, QModelIndex, Signal
from ankirestlib.anki_rest_client import *

class DeckModel(QAbstractListModel):
    TextRole = Qt.UserRole + 1
    TypeRole = Qt.UserRole + 2
    DidRole = Qt.UserRole + 3

    def __init__(self, anki_client):
        super().__init__()
        self.anki_client = anki_client

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()

        if role == DeckModel.TextRole:
            return self.decks[row].name
        if role == DeckModel.DidRole:
            return self.decks[row].id

    def roleNames(self):
        return {
            DeckModel.TextRole: b'text',
            DeckModel.TypeRole: b'type',
            DeckModel.DidRole: b'did'
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self.decks)

    @Slot(int, result=str)
    def getDid(self, index):
        print(self.decks[index].name)
        return str(self.decks[index].id)


class RegularDeckModel(DeckModel):
    def __init__(self, anki_client):
        super().__init__(anki_client)
        self.decks = anki_client.list_regular_decks()


class DynamicDeckModel(DeckModel):
    def __init__(self, anki_client):
        super().__init__(anki_client)
        self.decks = anki_client.list_dynamic_decks()


class NoteModel(QAbstractListModel):
    # UserRole = 0x0100, first role that can be used for application
    # specific purposes
    IdRole = Qt.UserRole + 1
    FrontRole = Qt.UserRole + 2
    BackRole = Qt.UserRole + 3

    def __init__(self, anki_client, parent=None):
        super().__init__(parent)
        self.anki_client = anki_client
        self.notes = anki_client.list_all_notes()

    # Each model has a set of data elements (roles) associated with it
    # Qt::DisplayRole = 0
    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if role == NoteModel.IdRole:
            return self.notes[row].id
        if role == NoteModel.FrontRole:
            return self.notes[row].front
        if role == NoteModel.BackRole:
            return self.notes[row].back
        # If no corrent value I should return a
        # qVariant here instead

    # Returns the number of rows under the given parent
    # QModelIndex() represents an empty model index and is used
    # to indicate an invalid value
    def rowCount(self, parent=QModelIndex()):
        return len(self.notes)

    def roleNames(self):
        return {
            NoteModel.IdRole: b'id',
            NoteModel.FrontRole: b'front',
            NoteModel.BackRole: b'back'
        }


    @Slot(str, str, str, str)
    def addNote(self, front, back, tags, deck_name):
        self.beginInsertRows(QModelIndex(),
                             self.rowCount(),
                             self.rowCount())
        decks = self.anki_client.list_all_decks()
        for deck in decks:
            if deck.name == deck_name:
                selected_deck = deck
                break
        if not selected_deck:
            print("Deck not found: " + selected_deck.name)
            return

        new_note = Note(front=front, back=back, tags=tags,
                        did=selected_deck.id)
        self.anki_client.add_note(new_note)
        # TODO: Check if appending note as a dict makes a difference
        # The response doesn't include the note id so have to get all notes again
        self.notes = self.anki_client.list_all_notes()
        self.endInsertRows()


class SortFilterNoteModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.firstRole = Qt.UserRole + 1
        self.setFilterRole(self.firstRole)
        self.setFilterRegExp("")  #self.setFilterRegExp("1518301088858")

    @Slot(str)
    def autoSort(self, column):
        role = self.firstRole + int(column)
        self.setSortRole(role)
        if self.sortOrder() == Qt.AscendingOrder:
            order = Qt.DescendingOrder
        else:
            order = Qt.AscendingOrder
        self.sort(0, order)
