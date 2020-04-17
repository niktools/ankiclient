import os
import sys
import argparse
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from ankirestlib.anki_rest_client import AnkiRestClient

from ankiclientapp.anki_qt_models import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server_url', dest='server_url')
    parser.add_argument('--collection', dest='collection')
    options = parser.parse_args()

    anki_client = AnkiRestClient(options.server_url, options.collection)

    notes = anki_client.list_all_notes()
    anki_client.delete_note(notes[0].id)
    notes = anki_client.list_all_notes()
    testnote = Note("test", "test2")
    anki_client.add_note(testnote)

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    note_model = NoteModel(anki_client)
    sorted_note_model = SortFilterNoteModel()
    sorted_note_model.setSourceModel(note_model)
    regular_deck_model = RegularDeckModel(anki_client)
    dynamic_deck_model = DynamicDeckModel(anki_client)
    engine.rootContext().setContextProperty("noteModel", note_model)
    engine.rootContext().setContextProperty("sortedNoteModel", sorted_note_model)
    engine.rootContext().setContextProperty("regDeckModel", regular_deck_model)
    engine.rootContext().setContextProperty("dynDeckModel", dynamic_deck_model)

    notes = anki_client.list_all_notes()

    qml_file = os.path.join(os.path.dirname(__file__), "MainWindow.qml")
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    app.exec_()


if __name__ == '__main__':
    main()