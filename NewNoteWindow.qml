import QtQuick 2.14
import QtQuick.Window 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls 1.4 as QC1

Window {
    width: 300
    height: 200

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        spacing: 5

        Column {
            Label {
                text: "Regular deck"
            }
            QC1.ComboBox {
                id: deckCombobox
                width: frontTextField.width
                height: 25
                textRole: "text" // Exact textRole is important otherwise it won't even call model.data()
                model: regDeckModel
                onCurrentIndexChanged: console.info("Fix so we keep track of dynamic and standard deck, enable/disable tags?")
            }
        }
        Column {
            Label {
                text: "Model"
            }
            QC1.ComboBox {
                width: frontTextField.width
                height: 25
                model: ["Basic"]
            }
        }
        Column {
            Label {
                text: "Front"
            }
            TextField {
                height: 25
                id: frontTextField
            }
        }
        Column {
            Label {
                text: "Back"
            }
            TextField {
                height: 25
                id: backTextField
            }
        }
        Column {
            Switch {
                id: filteredDeckTagsSwitch
                text: qsTr("Filtered Deck/Tags")
                onToggled: {
                    filteredDeckColumn.visible = !checked
                    tagsColumn.visible = checked
                }
            }
        }
        Column {
            id: filteredDeckColumn
            Label {
                text: "Filtered deck"
            }
            QC1.ComboBox {
                id: filteredDeckComboBox
                width: frontTextField.width
                height: 25
                textRole: "text" // Exact textRole is important otherwise it won't even call model.data()
                model: dynDeckModel
                onCurrentIndexChanged: console.info("Fix so we keep track of dynamic and standard deck, enable/disable tags?")
            }
        }
        Column {
            id: tagsColumn
            visible: false
            Label {
                text: "Tags"
            }
            TextField {
                height: 25
                id: tagsTextField
            }
        }
        Button {
            id: buttonAdd
            height: 30
            width: tagsTextField / 2
            text: "Add"

            onPressed: noteModel.addNote(frontTextField.text, backTextField.text,
                                         tagsTextField.text, deckCombobox.currentText)
        }
    }
}