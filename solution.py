from xxlimited import new
from sklearn import neighbors
import sys

def reverse_dictionary(original_dict):
    reverse_dict = {}
    
    for key, values in original_dict.items():
        for value in values:
            if value not in reverse_dict:
                reverse_dict[value] = []
            reverse_dict[value].append(key)
    
    return reverse_dict

class Agent(object):
    def __init__(self, phoneme_table, vocabulary) -> None:
        """
        Your agent initialization goes here. You can also add code but don't remove the existing code.
        """
        
        self.phoneme_table = reverse_dictionary(phoneme_table)
        self.vocabulary = vocabulary
        self.multi = 
        self.best_state = None
        print(self.phoneme_table)
        
    def generate_neighbors(self,text, phoneme_table, missing_words):
        words = text.split()
        neighbors = []
        
        # Character substitutions
        for i, word in enumerate(words):
            for j, char in enumerate(word):
                for replacement in phoneme_table.get(char, []):
                    neighbor_word = word[:j] + replacement + word[j+1:]
                    neighbor_words = words[:i] + [neighbor_word] + words[i+1:]
                    neighbors.append(" ".join(neighbor_words))
        
        # Insert missing words
        for missing_word in missing_words:
            neighbors.append(missing_word + " " + text)  # Add at the beginning
            neighbors.append(text + " " + missing_word)  # Add at the end
        
        return neighbors
    
    
    def asr_corrector(self, environment):
        """
        Your ASR corrector agent goes here. Environment object has following important members.
        - environment.init_state: Initial state of the environment. This is the text that needs to be corrected.
        - environment.compute_cost: A cost function that takes a text and returns a cost. E.g., environment.compute_cost("hello") -> 0.5

        Your agent must update environment.best_state with the corrected text discovered so far.
        """
        self.best_state = environment.init_state
        best_cost = environment.compute_cost(environment.init_state)
        # print(environment.compute_cost("SHE FOLBED AMONG THE FLICKEWING SHADOWS A GRACEFUL AND HARMONIOUS IMAGE"))
        # print(environment.compute_cost("SHE FOLBED AMONG THE FLICKERING SHADOWS A GRACEFUL AND HARMONIOUS IMAGE"))
        # sys.exit()
        improved = True
        while(improved):
            improved = False
            words = self.best_state.split()
            
            # for i,word in enumerate(words):
            #     neighbors = self.generate_neighbors(word,self.phoneme_table, [])
            #     new_words = self.best_state.split()
                
            #     for neighbor in neighbors:
            #         new_words[i] = neighbor
            #         new_state = " ".join(new_words)
            #         new_cost = environment.compute_cost(new_state)
            #         print(new_state)
            #         print(new_cost, best_cost)
                    
                    # if new_cost < best_cost:
                    #     self.best_state = new_state
                    #     best_cost = new_cost
                    #     improved = True
                    #     print(self.best_state)
            for i, word in enumerate(words):
                char_list = list(word)
                print(char_list)
                new_words = self.best_state.split()
                for j, char in enumerate(word):
                    best_char = char
                    if char in self.phoneme_table:
                        neighbors = self.phoneme_table[char]
                        # neighbors.append(char)
                        for neighbor in neighbors:
                            char_list[j] = neighbor
                            new_word = "".join(char_list)
                            new_words[i] = new_word
                            new_state = " ".join(new_words)
                            new_cost = environment.compute_cost(new_state)
                            print(new_state)
                            print(new_cost, best_cost, char, neighbor)
                            
                            if new_cost < best_cost:
                                best_char = neighbor
                                self.best_state = new_state
                                best_cost = new_cost
                                # improved = True
                    
                    char_list[j] = best_char
                    new_word = "".join(char_list)
                    new_words[i] = new_word
                        
        return self.best_state
