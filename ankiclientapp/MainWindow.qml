import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Controls 1.4 as QC1

ApplicationWindow {
    id: root
    visible: true
    width: 640
    height: 480

    property variant addCardWindow;
    property variant addDeckWindow;
    
    background: Rectangle {
        color: "darkGray"
    }
    Item {
        id: toolbar
        height: 20
        width: parent.width
        QC1.Button {
            id: addCardButton
            height: parent.height
            width: 80
            text: "Add"
            anchors.left: parent.left
            onClicked: {
                var component = Qt.createComponent("NewNoteWindow.qml");
                addCardWindow = component.createObject(root);
                addCardWindow.show();
            }
        }
        QC1.Button {
            id: addMultipleCardsButton
            height: parent.height
            width: 80
            text: "Add cards"
            anchors.left: addCardButton.right
        }
         QC1.Button {
            id: addDeckButton
            height: parent.height
            width: 80
            text: "Add deck"
            anchors.left: addMultipleCardsButton.right
            onClicked: {
                var component = Qt.createComponent("NewDeckWindow.qml");
                addDeckWindow = component.createObject(root);
                addDeckWindow.show();
            }
        }


        QC1.ComboBox {
            id: comboboxDecks
            width: 200
            height: parent.height
            anchors.left: addDeckButton.right
            textRole: "text" // Exact textRole is important otherwise it won't even call model.data()
            model: regDeckModel //[ "Banana", "Apple", "Coconut" ]
            onCurrentIndexChanged: {
                tableView.model.setFilterRegExp(regDeckModel.getDid(comboboxDecks.currentIndex))
            }
        }
    }

    QC1.TableView {
        id: tableView
        width: parent.width
        height: parent.height*0.8
        model: sortedNoteModel
        anchors.top: toolbar.bottom
        sortIndicatorVisible: true
        onSortIndicatorColumnChanged:
        {
            model.autoSort(sortIndicatorColumn)
        }
        onSortIndicatorOrderChanged:
        {
            model.autoSort(sortIndicatorColumn)
        }
        QC1.TableViewColumn {
            id: idColumn
            role: "id"
            title: "id"
            width: 100
        }
        QC1.TableViewColumn {
            id: frontColumn
            role: "front"
            title: "front"
            width: 100
        }
        QC1.TableViewColumn {
            id: backColumn
            role: "back"
            title: "back"
            width: tableView.viewport.width - idColumn.width - frontColumn.width
        }
    }
}


