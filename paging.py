# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 11:13:39 2019

@author: scatt

OS Assignment 4 - Page Replacement Algorithms
Due: Thursday 11-Apr 2019

"""

import csv
import random
from random import randint
from collections import OrderedDict


def show_results(alg, h, m):
    print("\nAlgorithm:\t"+alg+"\nHits:\t\t"+str(h)+"\nMisses:\t\t"+str(m))
    print("\nPage fault percentage: "+str(((m)/(m+h))*100)+"%")
    print("\n-----------------------------------------------------")
    

def fifo(refs, page_table_size):
    page_table = OrderedDict()
    oldest_key = []
    hits = 0
    misses = 0
    for ref in refs:
        if ref[0] in page_table:
            hits += 1
        else:
            misses += 1
            if len(page_table) < page_table_size:
                page_table[ref[0]] = (ref[1], ref[2])
                oldest_key.append(ref[0])
            else:
                page_table.pop(oldest_key.pop(0))
                page_table[ref[0]] = (ref[1], ref[2])
                oldest_key.append(ref[0])
                
    show_results("First in first out", hits, misses)
    

def nru(refs, page_table_size):
    #print('\n'.join(str(ref) for ref in refs))
    hits = 0
    misses = 0
    page_table = OrderedDict()
    for ref in refs:                                # assuming page arrival times are monotonically increasing
        if ref[0] in page_table:
            hits += 1
            if page_table[ref[0]][1] == 'R':
                page_table[ref[0]][2] = 1
                page_table[ref[0]][3] = 0
            else:
                page_table[ref[0]][2] = 1
                page_table[ref[0]][3] = 1
        else:
            misses += 1
            if len(page_table) < page_table_size:   # page fault, but page table is NOT full so just add the page
                page_table[ref[0]] = [ref[1], ref[2], ref[3], ref[4], ref[5]]
            else:                                   # page table is full and another page must be evicted
                lowest_class = 3
                for key in page_table:              # find the lowest NRU class in memory (page table)
                    if page_table[key][2] == 0 and page_table[key][3] == 0:
                        lowest_class = 0
                        page_table[key][4] = 0
                    elif page_table[key][2] == 0 and page_table[key][3] == 1:
                        lowest_class = 1
                        page_table[key][4] = 1
                    elif page_table[key][2] == 1 and page_table[key][3] == 0:
                        lowest_class = 2
                        page_table[key][4] = 2
                    else:
                        lowest_class = 3
                        page_table[key][4] = 3
                key_to_remove = 0
                for key in page_table:
                    if page_table[key][4] == lowest_class:  # found page to evict
                        key_to_remove = key
                        break                               # take first key that matches to reduce time complexity
                        
                page_table.pop(key_to_remove)               # evict page given by specified key
                page_table[ref[0]] = [ref[1], ref[2], ref[3], ref[4], ref[5]]
                
    show_results("Not Recently Used", hits, misses)
                        

def second_chance(refs_original, page_table_size):
    hits = 0
    misses = 0
    page_table = OrderedDict()
    refs = []
    for item in refs_original:                              # get rid of unnecessary bits and append a new "referenced" bit
        item = item[0:3] + [0]
        refs.append(item)
    for ref in refs:
        #print('\n',page_table)
        #print(len(page_table))
        #print("Inserting page "+str(ref[0]))
        if ref[0] in page_table:
            hits += 1
            page_table[ref[0]][2] = 1
            #print("FOUND: page "+str(ref[0]))
        else:
            misses += 1
            if len(page_table) >= page_table_size:
                # find page to evict
                page_to_evict = -1
                shift_count = 0
                for key in page_table:
                    if page_table[key][2] == 0:
                        page_to_evict = key
                        #print("found page to evict: "+key)
                        break
                    else:
                        page_table[key][2] = 0
                        shift_count += 1
                for i in range(shift_count):
                    temp = page_table.popitem(last=False)
                    #print('old front: ',temp)
                    page_table[temp[0]] = temp[1]
                    #print('now at back: '+str(page_table[temp[0]]))
                page_table.pop(page_to_evict)
                page_table[ref[0]] = [ref[1], ref[2], ref[3]]
            else:
                page_table[ref[0]] = [ref[1], ref[2], ref[3]]
        
    show_results("Second chance", hits, misses)

def aging(refs_original, page_table_size):
    hits = 0
    misses = 0
    page_table = OrderedDict()
    refs = []
    for item in refs_original:                              # get rid of unnecessary bits and append a reference counter
        item = item[0:3] + [0]
        refs.append(item)
    for ref in refs:
        if ref[0] in page_table:
            hits += 1
            for key in page_table:
                if page_table[key][2] > 0 and key != ref[0]:
                    page_table[key][2] -= 1
            page_table[key][2] += 50
        else:
            misses += 1
            if len(page_table) >= page_table_size:
                min_ref_count = 1 << 50                     # arbitrarily-high ref count to ensure nothing exceeds
                page_to_evict = -1
                for key in page_table:
                    if page_table[key][2] < min_ref_count:
                        min_ref_count = page_table[key][2]
                        page_to_evict = key
                        
                page_table.pop(page_to_evict)
                page_table[ref[0]] = [ref[1], ref[2], ref[3]]
            else:
                page_table[ref[0]] = [ref[1], ref[2], ref[3]]
                
    show_results("Aging", hits, misses)
    
def optimal(refs_original, page_table_size):
    refs = [item for item in refs_original]                 # make copy so as to not delete list for other algs
    hits = 0
    misses = 0
    page_table = OrderedDict()
    while len(refs) > 0:
        ref = refs[0]
        if ref[0] in page_table:
            hits += 1
#            print("Found "+str(ref[0])+" in page table")
        else:
            misses += 1
            if len(page_table) >= page_table_size:
#                print(str(ref[0])+" not found. choosing page to evict...")
                # CHOOSE PAGE TO EVICT, AND EVICT
                page_to_evict = 0
                dist = 0
                for key in page_table:
                    found = False
                    for i, r in enumerate(refs[1:]):
                        if r[0] == key:
#                            print("key "+str(key)+" was found with distance "+str(i))
                            found = True
                            if i > dist:
                                page_to_evict = key
                                dist = i
                                break
                    if not found:
#                        print("since "+str(key)+" was not found, evicting")
                        page_to_evict = key
                        break
#                print("evicting page "+str(page_to_evict))
                page_table.pop(page_to_evict)
                page_table[ref[0]] = [ref[1], ref[2]]
            else:
#                print("available space; inserting page "+str(ref[0]))
                page_table[ref[0]] = [ref[1], ref[2]]
        refs.pop(0)
        
    show_results("Optimal", hits, misses)
    

# utility function to perform linear search for int key within a list (return index if key found in list)
def scan_list(ls, key):
    for index, item in enumerate(ls):
        if key == item[0]:
            return index
    return -1
    
        
def wait_and_confirm(refs_original, page_table_size):
    hits = 0
    misses = 0
    page_table = OrderedDict();
    temp_table = []
    tt_max_size = page_table_size // 10             # temp table is 10% as large as the full page table (max)
    refs = []
    for item in refs_original:
        refs.append(item[0:4])                      # 3 usual bits + 1 for "confirmation" bit, init. to 0
    for ref in refs:
        if len(temp_table) < tt_max_size:
            tmp = scan_list(temp_table, ref[0])
            if tmp != -1:
                hits += 1
                continue
            temp_table.append(ref)
            misses += 1
        else:
            val = scan_list(temp_table, ref[0])
            if val != -1:                           # page hit in the temp table
                temp = temp_table.pop(val)
                temp[3] = 1                         # set  confirmation bit to indicate locality reference
                hits += 1
                if temp[0] in page_table:
                    continue                        # to prevent evicting a 'good' page
                flag = False
                if len(page_table) < page_table_size:
                    page_table[temp[0]] = [temp[1], temp[2], temp[3]]
                else:
                    for key in page_table:
                        if page_table[key][2] == 0:
                            page_table.pop(key)
                            flag = True
                            break
                    if not flag:
                        for key in page_table:
                            page_table.pop(key)         # pop first item, since all pages in page table were already "confirmed"
                            break
                    page_table[temp[0]] = [temp[1], temp[2], temp[3]]
            else:
                if ref[0] in page_table:
                    hits += 1
                else:
                    misses += 1
                    if len(page_table) < page_table_size:
                        page_table[ref[0]] = [ref[1], ref[2], ref[3]]
                    else:                           # evict first non-confirmed page
                        flag = False
                        for key in page_table:
                            if page_table[key][2] == 0:
                                page_table.pop(key)
                                flag = True
                                page_table[ref[0]] = [ref[1], ref[2], ref[3]]
                                break
                        if not flag:
                            for key in page_table:
                                page_table.pop(key)
                                page_table[ref[0]] = [ref[1], ref[2], ref[3]]
                                break

    show_results("Wait and Confirm", hits, misses)
                        
                        
                    
                
                
                

def main(in_file, page_table_size):
    refs = []
    with open(in_file) as fd:
        rd = csv.reader(fd, delimiter='\t')
        for row in rd:
            row.append(0)                           # append two bits to represent "referenced" and "modified"
            row.append(0)
            row.append(0)                           # append another bit to represent the NRU class
            refs.append(row)
            
    # LIST OF PAGE REPLACEMENT ALGORITHMS (uncomment one at a time)
    #print('\n'.join(str(ref) for ref in refs))
    
    optimal(refs, page_table_size)
    fifo(refs, page_table_size)
    nru(refs, page_table_size)
    second_chance(refs, page_table_size)
    aging(refs, page_table_size)
    wait_and_confirm(refs, page_table_size)            # my own algorithm; see report or implementation details in function

    
def generate_file(num_references, max_page_num):
    ref_time_inc_max = 5
    ref_type = ['R','W']
    start_time = 0
    out_file = 'references'+str(num_references)+'.txt'
    
    with open(out_file,'w',newline='') as f:
        for i in range(num_references):
            temp = []
            temp.append(randint(1,max_page_num))
            temp.append(start_time)
            start_time += randint(1,ref_time_inc_max)
            temp.append(random.choice(ref_type))
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(temp)
    
    return out_file

                     
if __name__ == "__main__":
    page_table_size = 100
    num_references = 1000
    max_page_num = 150
    file = generate_file(num_references, max_page_num)
    main(file, page_table_size)