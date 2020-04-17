import QtQuick 2.14
import QtQuick.Window 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls 1.4 as QC1

Window {
    id: newNoteWindow
    width: 300
    height: 200

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        spacing: 5

        Column {
            Label {
                text: "Name"
            }
            TextField {
                height: 25
                id: deckNameField
            }
        }
        Column {
            Label {
                text: "Tags"
            }
            TextField {
                height: 25
                id: deckTagsField
            }
        }
        Button {
            id: buttonAdd
            height: 30
            width: deckTagsField / 2
            text: "Add"

            onPressed: {
            }
        }
    }
}