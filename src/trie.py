from typing import Optional, Tuple


class Trie:
    def __init__(self):
        self.children = {}
        self.value = None
    
    def search_longest(self, s, i = 0) -> Tuple[Optional[object], int]:
        curr = self
        j = i
        out = ( None, i )
        while(curr != None and j < len(s)):
            out = ( curr.value, j )
            curr_letter = s[j]

            if(curr_letter not in curr.children):
                return out
            
            curr = curr.children[curr_letter]
            j += 1

        return ( curr.value, j )
        
    def insert(self, s: str, value, i=0):
        if(len(s) == i):
            self.value = value
            return
        curr_letter = s[i]
        if(curr_letter not in self.children):
            self.children[curr_letter] = Trie()
        self.children[curr_letter].insert(s, value, i+1)
