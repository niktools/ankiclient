#!/usr/bin/env python
# -*- conding: utf-8 -*-

import os
import sys
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from anki_client.ankirestclient import AnkiRestClient


def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    anki_client = AnkiRestClient("http://localhost:8051", "niknil1")

    note_model = NoteModel(anki_client)
    sorted_note_model = SortFilterNoteModel()
    sorted_note_model.setSourceModel(note_model)
    regular_deck_model = RegularDeckModel(anki_client)
    dynamic_deck_model = DynamicDeckModel(anki_client)
    engine.rootContext().setContextProperty("noteModel", note_model)
    engine.rootContext().setContextProperty("sortedNoteModel", sorted_note_model)
    engine.rootContext().setContextProperty("regDeckModel", regular_deck_model)
    engine.rootContext().setContextProperty("dynDeckModel", dynamic_deck_model)

    qml_file = os.path.join(os.path.dirname(__file__), "MainWindow.qml")
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    app.exec_()


if __name__ == '__main__':
    main()