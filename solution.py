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
        self.multi = [key for key in self.phoneme_table.keys() if len(key) > 1]
        self.best_state = None
        self.result_dict = {}
        for element in self.multi:
            first_letter = element[0]      # Extract the first letter
            
            # Add to the dictionary or append to the existing list
            if first_letter in self.result_dict:
                self.result_dict[first_letter].append(element)
            else:
                self.result_dict[first_letter] = [element]
        
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
    
    
    def find_all_occurrences(text, segment):
        indices = []
        start = 0
        while True:
            start = text.find(segment, start)
            if start == -1:
                break
            indices.append(start)
            start += 1  # Move past the last found occurrence
        return indices
    
    def asr_corrector(self, environment):
        """
        Your ASR corrector agent goes here. Environment object has following important members.
        - environment.init_state: Initial state of the environment. This is the text that needs to be corrected.
        - environment.compute_cost: A cost function that takes a text and returns a cost. E.g., environment.compute_cost("hello") -> 0.5

        Your agent must update environment.best_state with the corrected text discovered so far.
        """
        self.best_state = environment.init_state
        best_cost = environment.compute_cost(environment.init_state)
        improved = True
        txt = self.best_state

        
        front_word = ""
        print(self.vocabulary)
        
        # adding first word in the dictionary
        for vocab_word in self.vocabulary:
                new_state_start = vocab_word + " " + self.best_state
                new_cost_start = environment.compute_cost(new_state_start)
                print(new_state_start)
                print(vocab_word,new_cost_start, best_cost )
                if(new_cost_start < best_cost):
                    # front_add = True
                    best_cost = new_cost_start
                    front_word = vocab_word
                    # print(new_state_start)
        if(front_word != ""):
            front_word += " "
            
        
        changed_txt = [False]*(len(txt))
        char_list = list(txt)
        char_list_copy = char_list.copy()
        wait_list = [0]*(len(txt))
        multi_char = [""] * (len(txt))
        reverse = False
        
        while(improved):
            improved = False
            for i in range(len(txt)):
                if(reverse):
                    i = len(txt)-1 - i
                char = char_list[i]
                best_char = char
                if(changed_txt[i] or char == ' ' or char_list[i] == ""):
                    continue
                else:
                    if(wait_list[i] == 1):
                        print(char_list[i])
                        print("here")
                        wait_list[i] = 0
                        improved = True
                        # sys.exit()
                        continue
                            
                if char in self.phoneme_table:
                    print(char)
                    neighbors = self.phoneme_table[char]
                    for neighbor in neighbors:
                        char_list[i] = neighbor
                        new_state = "".join(char_list)
                        new_cost = environment.compute_cost((front_word + new_state))
                        print((front_word + new_state))
                        print(new_cost, best_cost, char, neighbor)
                        
                        if new_cost < best_cost:
                            changed_txt[i] = True
                            best_char = neighbor
                            self.best_state = new_state
                            best_cost = new_cost
                            improved = True
                            # print((front_word + new_state))
                            # print(new_cost, best_cost, char, neighbor)
                    
                char_list[i] = best_char
                if char in self.result_dict:
                    for segment in self.result_dict[char]:
                        start = txt.startswith(segment, i)
                        if not(start):
                            continue
                        else:
                            changed = False
                            print(segment)
                            x = len(segment)
                            store = ""
                            best_char = char
                            for k in range(1,x):
                                store += char_list[i+k]
                            for k in range(1,x):
                                char_list[i+k] = ""
                            for neighbor in self.phoneme_table[segment]:
                                char_list[i] = neighbor
                                new_state = "".join(char_list)
                                new_cost = environment.compute_cost((front_word + new_state))
                                print((front_word + new_state))
                                print(new_cost, best_cost, segment, neighbor)
                                if new_cost < best_cost:
                                    store = ""
                                    improved = True
                                    changed = True
                                    best_char = neighbor
                                    self.best_state = new_state
                                    best_cost = new_cost
                                    # print((front_word + new_state))
                                    # print(new_cost, best_cost, segment, neighbor)
                            if(not(changed)):
                                for k in range(1,x):
                                    char_list[i+k] = store[k-1]
                            else:
                                for k in range(x):
                                    changed_txt[i+k] = True
                                    multi_char[i+k] = " "
                                multi_char[i] = segment
                                print(multi_char[i])
                            char_list[i] = best_char
                                
            
            for i in range(len(char_list_copy)):
                if(not(changed_txt[i]) or multi_char[i] == " "):
                    continue
                is_multi = False
                if(multi_char[i] == ""):
                    c = char_list[i]
                    char_list[i] = char_list_copy[i]
                    
                else:
                    is_multi = True
                    c = char_list[i]
                    seg = multi_char[i]
                    segment_length = len(seg)
                    for j in range(segment_length):
                        char_list[i+j] = seg[j]
                new_state = "".join(char_list)
                new_cost = environment.compute_cost((front_word + new_state))
                print((front_word + new_state))
                print(new_cost, best_cost, c, char_list_copy[i])
                if new_cost >= best_cost + 0.05:
                    if(is_multi):
                        char_list[i] = c
                        for j in range(1,segment_length):
                            char_list[i+j] = ""
                    else:
                        char_list[i] = c
                else:
                    self.best_state = new_state
                    best_cost = new_cost
                    changed_txt[i] =False
                    # wait_list[i] = 1
                    if(is_multi):
                        multi_char[i] = ""
                        for j in range(1,segment_length):
                            changed_txt[i+j] = False
                            # wait_list[i+j] = 1
                            multi_char[i+j] = ""
                new_state = "".join(char_list)
            # sys.exit() 
            reverse = not(reverse)    
             
        self.best_state = front_word + self.best_state
        
        last_word = ""
        for vocab_word in self.vocabulary:
                new_state_end = self.best_state + " " + vocab_word
                new_cost_end = environment.compute_cost(new_state_end)
                print(new_state_end)
                print(vocab_word,new_cost_end, best_cost )
         
                if new_cost_end < best_cost:
                    best_cost = new_cost_end
                    last_word = vocab_word
                    # print(new_state_end)
                    # print(vocab_word,new_cost_end, best_cost )
        if(last_word != ""):
            self .best_state = self.best_state + " " + last_word
        
        n = len(front_word)
        s = self.best_state[n:]
        cost = environment.compute_cost(s)
        print(s)
        print(cost, best_cost)
        if(cost < best_cost):
            self.best_state = s
        return self.best_state
