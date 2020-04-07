#!/usr/bin/env python
# -*- conding: utf-8 -*-

import os
import sys
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import QAbstractTableModel, QSortFilterProxyModel, QAbstractListModel, Qt, Slot, QModelIndex
from AnkiClient import AnkiClient
import pdb
from myrestrequester.ankirestclient import AnkiRestClient, Note, DynamicDeck, RegularDeck


class DeckModel(QAbstractListModel):
    TextRole = Qt.UserRole + 1
    TypeRole = Qt.UserRole + 2

    def __init__(self, ankiclient):
        super().__init__()
        self.ankiclient = ankiclient
        self.testaval = 5

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()

        if role == DeckModel.TextRole:
            return self.decks[row].name

    def roleNames(self):
        return {
            DeckModel.TextRole: b'text',
            DeckModel.TypeRole: b'type'
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self.decks)


class RegularDeckModel(DeckModel):
    def __init__(self, ankiclient):
        super().__init__(ankiclient)
        self.decks = ankiclient.list_regular_decks()


class DynamicDeckModel(DeckModel):
    def __init__(self, ankiclient):
        super().__init__(ankiclient)
        self.decks = ankiclient.list_dynamic_decks()


class NoteModel(QAbstractListModel):
    # UserRole = 0x0100, first role that can be used for application
    # specific purposes
    IdRole = Qt.UserRole + 1
    FrontRole = Qt.UserRole + 2
    BackRole = Qt.UserRole + 3

    def __init__(self, ankiclient, parent=None):
        super().__init__(parent)
        self.ankiclient = ankiclient
        self.notes = ankiClient.listAllNotes()

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

    # Must be slot to be accessible from qml
    @Slot(str, str, str)
    def addPerson(self, did, question, answer):
        # begigInsertRows and endInsertRows emits signals that the view
        # uses to remain in a consistent state
        self.beginInsertRows(QModelIndex(),
                             self.rowCount(),
                             self.rowCount())
        self.notes.append({'did': did, 'question': question, 'answer': answer})
        self.endInsertRows()

    @Slot(int, str, str, str)
    def editPerson(self, row, name, code, language):
        ix = self.index(row, 0)
        self.persons[row] = {'name': name, 'code': code, 'language': language}
        self.dataChanged.emit(ix, ix, self.roleNames())

    @Slot(int)
    def deletePerson(self, row):
        self.beginRemoveColumns(QModelIndex(), row, row)
        del self.notes[row]
        self.endRemoveRows()

    @Slot(int, int)
    def sort(self, test, testa):
        print("HEJ", test, testa)

    @Slot(str, str, str, str)
    def addNote(self, front, back, tags, deck_name):
        decks = self.ankiclient.listDecks()
        for deck in decks:
            if deck.name == deck_name:
                selected_deck = deck
                break
        if not selected_deck:
            print("Deck not found: " + selected_deck.name)
            return

        new_note = Note(front=front, back=back, tags=tags,
                        did=selected_deck.id)
        self.ankiclient.addNote(new_note)


class SortProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.firstRole = Qt.UserRole + 1
        self.setFilterRole(self.firstRole)
        self.setFilterRegExp("1518301088858")

    @Slot(str)
    def autoSort(self, column):
        role = self.firstRole + int(column)
        self.setSortRole(role)
        if self.sortOrder() == Qt.AscendingOrder:
            order = Qt.DescendingOrder
        else:
            order = Qt.AscendingOrder
        self.sort(0, order)


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    ankiClient = AnkiRestClient("http://localhost:8051")
    #ankiClient = AnkiRestClient("http://localhost:27701")
    ankiClient.selectCollection("niknil")
    #ar = ankiClient.listAllCards()
    #ankiClient.selectDeck(1521380119606)
    #allDecks = ankiClient.listDecks()
    #testNote = Note(front="Bajs", back="Poop", model="Basic", tags="", did=1558860095136)
    #ankiClient.addNote(testNote)
    #allCards = ankiClient.listAllCards()
    #allDecks = ankiClient.listDecks()
    #allDecks = ankiClient.listDecks()

    noteModel = NoteModel(ankiClient)

    sortedNoteModel = SortProxyModel()
    sortedNoteModel.setSourceModel(noteModel)

    regular_deck_model = RegularDeckModel(ankiClient)
    dynamic_deck_model = DynamicDeckModel(ankiClient)
    engine.rootContext().setContextProperty("noteModel", noteModel)
    engine.rootContext().setContextProperty("sortedNoteModel", sortedNoteModel)
    engine.rootContext().setContextProperty("regDeckModel", regular_deck_model)
    engine.rootContext().setContextProperty("dynDeckModel", dynamic_deck_model)

    qml_file = os.path.join(os.path.dirname(__file__),"view.qml") #engine.load(QUrl("main.qml"))
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    app.exec_()
