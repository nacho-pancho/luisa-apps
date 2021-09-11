#!/usr/bin/python3
#By Steve Hanov, 2011. Released to the public domain
import time
import sys

#=============================================================================

INSERT_COST = 2
DELETE_COST = 2
REPLACE_COST = 1

# Keep some interesting statistics
node_count = 0
word_count = 0

#=============================================================================

# The Trie data structure keeps a set of words, organized with one node for
# each letter. Each node has a branch for each letter that may follow it in the
# set of words.
class TrieNode:
    def __init__(self):
        self.word = None
        self.children = {}

        global node_count
        node_count += 1

    #-------------------------------------------------------------------------

    def insert( self, word ):
        node = self
        for letter in word:
            if letter not in node.children: 
                node.children[letter] = TrieNode()

            node = node.children[letter]

        node.word = word

#=============================================================================

class DicSearch:
    def __init__(self,list_of_words):
        # read dictionary file into a trie
        self.trie = TrieNode()
        for word in list_of_words:
            self.trie.insert(word.strip())

    # -----------------------------------------------------------------------------

    def search( self, word, maxCost ):
        '''
        Return list of words that are less than the distance from the target word
        '''

        # build first row
        currentRow = list(range( len(word) + 1))

        results = []

        # recursively search each branch of the trie
        for letter in self.trie.children:
            self.__search_recursive( self.trie.children[letter], letter, word, currentRow,
                results, maxCost )

        return results

    # -----------------------------------------------------------------------------

    # This recursive helper is used by the search function above. It assumes that
    # the previousRow has been filled in already.
    def __search_recursive( self, node, letter, word, previousRow, results, maxCost ):

        columns = len( word ) + 1
        currentRow = [ previousRow[0] + 1 ]

        # Build one row for the letter, with a column for each letter in the target
        # word, plus one for the empty string at column 0
        for column in range( 1, columns ):

            #insertCost = currentRow[column - 1] + 1
            #deleteCost = previousRow[column] + 1
            insertCost = currentRow[column - 1] + INSERT_COST
            deleteCost = previousRow[column]    + DELETE_COST

            if word[column - 1] != letter:
                replaceCost = previousRow[ column - 1 ] + REPLACE_COST
            else:
                replaceCost = previousRow[ column - 1 ]

            currentRow.append( min( insertCost, deleteCost, replaceCost ) )

        # if the last entry in the row indicates the optimal cost is less than the
        # maximum cost, and there is a word in this trie node, then add it.
        if currentRow[-1] <= maxCost and node.word is not None:
            results.append( (node.word, currentRow[-1] ) )

        # if any entries in the row are less than the maximum cost, then
        # recursively search each branch of the trie
        if min( currentRow ) <= maxCost:
            for letter in node.children:
                self.__search_recursive( node.children[letter], letter, word, currentRow,
                    results, maxCost )

#=============================================================================

if __name__ == "__main__":
    TARGET = sys.argv[1]
    MAX_COST = int(sys.argv[2])
    start = time.time()
    search = DicSearch("dict.txt")
    results = search.search( TARGET, MAX_COST )
    end = time.time()

    for result in results: 
        print(result)        

    print("Search took %g s" % (end - start))

#=============================================================================
