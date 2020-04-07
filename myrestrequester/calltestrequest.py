from ankirestclient import AnkiRestClient

ankiClient = AnkiRestClient("http://localhost:27701")
ankiClient.selectCollection("niknil")


# Todo authorization

#hej = ankiClient.listDecks()
#print(hej)
#ankiClient.selectDeck("bla")
ar = ankiClient.listAllCards()
print("hej")
