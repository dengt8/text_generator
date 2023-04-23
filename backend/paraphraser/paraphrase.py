from nltk.tree import Tree
from itertools import permutations, product
from copy import deepcopy
import re
import json

def get_indexes_to_shuffle(tree : Tree, CHUNK_LABEL : str, CHUNK_LEAVES : list) -> dict:
    '''
    return indexes of nodes for shuffling for new sentences as dictionary,
    where key is parent node and value is index to get access to tree
    
    tree : a hierarchical grouping of leaves and subtrees from nltk library
    
    >>> get_indexes_to_shuffle(
    ... Tree.fromstring('(S (NP (NP (DT The) (JJ charming) (NNP Gothic) (NNP Quarter) )\
    (, ,) (CC or) (NP (NNP Barri) (NNP Gòtic) ) ) )'),
    ... 'NP',
    ... ["NP", ",", "CC"])
    {'[0]': ['00', '03']}
    '''

    def is_conditions_followed(node_label : str, tree : Tree, CHUNK_LABEL : str, CHUNK_LEAVES : list, parent_index : str) -> bool:
        '''
        return True if parent node, current node and its leaves follow the conditions

        node_label : a subtree name
        tree : a hierarchical grouping of leaves and subtrees from nltk library
        CHUNK_LABEL : a subtree name for check
        CHUNK_LEAVES : leaves names for check
        parent_index : index to get data from tree on one level higher

        >>> is_conditions_followed(
        ... 'NP', 
        ... Tree.fromstring('(S (NP (NP (DT The) (JJ charming) (NNP Gothic) (NNP Quarter) ) \
        ...     (, ,) (CC or) (NP (NNP Barri) (NNP Gòtic) ) ) )'),
        ... 'NP', 
        ... ["NP", ",", "CC"], 
        ... '[0]')
        True
        '''
        return node_label == CHUNK_LABEL \
            and eval(f'tree{parent_index}.label()') == CHUNK_LABEL \
            and eval(f'all(chunk in {CHUNK_LEAVES} for chunk in [t.label() for t in tree{parent_index}])')

    def get_parent_index(current_position : str) -> str:
        '''
        return new genereted index for access tree data on one level higher
        
        current_position : string index to get data from tree

        >>> get_parent_index('123')
        '[1][2]'
        >>> get_parent_index('0034')
        '[0][0][3]'
        '''
        return ''.join(list(f'[{i}]' for i in current_position[:-1]))

    def walk_nodes(parent : Tree, index='') -> None:
        '''
        recursion like depth-first search for walk and check every node for conditions
        
        parent : a hierarchical grouping of leaves and subtrees from nltk library
        index : position from current node
        '''
        for i, node in enumerate(parent):
            if type(node) is Tree:
                new_index = index + str(i)
                parent_index = get_parent_index(new_index)
                if is_conditions_followed(node.label(), tree, CHUNK_LABEL, CHUNK_LEAVES, parent_index):
                    if not parent_index in nodes:
                        nodes[parent_index] = list()
                    nodes[parent_index].append(new_index)
                walk_nodes(node, new_index)
    
    nodes = {}
    walk_nodes(tree)
    return nodes

def get_permutations(indexes : dict, limit=20) -> list:
    '''  
    return list of list with unique permutations of indexes
    
    indexes : dictionary, where key is parent node and value is index to get access to tree
    limit: limit of return - maximal length of list with permutations, 20 by default
    
    >>> get_permutations({'[0]': ['00', '03']})
    [['00', '03'], ['03', '00']]
    
    >>> get_permutations({'[0]': ['00', '03']}, limit=1)
    [['00', '03']]
    '''
    shifts = []
    shifts = list(product(*[list(permutations(n)) for n in list(indexes.values())]))
    shifts = list(list(inner_tupl for tupl in shi for inner_tupl in tupl) for shi in shifts)
    return shifts[:limit]

def get_paraphrases(tree: Tree, limit=20, output='tree'):  
    '''
    return all possible paraphrases of original tree in json format by default
    
    tree: a bracketed tree string such as (S (NP (NNP John)) (VP (V runs)))
    limit: limit of return - maximal length of json or list with paraphrases, 20 by default
    output: format of return - as tree by default or as json, usual text. Usage : output='tree', output='json', output='text'
    
    >>> get_paraphrases('(S (NP (NP (DT The) (JJ charming) (NNP Gothic) (NNP Quarter) ) (, ,) (CC or) (NP (NNP Barri) \
    (NNP Gotic) ) ) )', limit=2)
    ['(S (NP (NP (DT The) (JJ charming) (NNP Gothic) (NNP Quarter)) (, ,) (CC or) (NP (NNP Barri) (NNP Gotic))))', '(S (NP (NP (NNP Barri) (NNP Gotic)) (, ,) (CC or) (NP (DT The) (JJ charming) (NNP Gothic) (NNP Quarter))))']
    
    >>> get_paraphrases('(S (NP (NP (DT The) (JJ charming) (NNP Gothic) (NNP Quarter) ) (, ,) (CC or) (NP (NNP Barri) \
    (NNP Gotic) ) ) )' , output = 'json')
    '{"paraphrases": [{"tree": "(S (NP (NP (DT The) (JJ charming) (NNP Gothic) (NNP Quarter)) (, ,) (CC or) (NP (NNP Barri) (NNP Gotic))))"}, {"tree": "(S (NP (NP (NNP Barri) (NNP Gotic)) (, ,) (CC or) (NP (DT The) (JJ charming) (NNP Gothic) (NNP Quarter))))"}]}'
    
    >>> get_paraphrases('(S (NP (NP (DT The) (JJ charming) (NNP Gothic) (NNP Quarter) ) (, ,) (CC or) (NP (NNP Barri) \
    (NNP Gotic) ) ) )', limit=2, output='text')
    ['The charming Gothic Quarter , or Barri Gotic', 'Barri Gotic , or The charming Gothic Quarter']
    '''
    
    tree = Tree.fromstring(tree)
    CHUNK_LABEL = 'NP'
    CHUNK_LEAVES = ["NP", ",", "CC"]

    indexes = get_indexes_to_shuffle(tree, CHUNK_LABEL, CHUNK_LEAVES)
    permutations = get_permutations(indexes, int(limit))

    new_tree = deepcopy(tree)
    code_shifts = []
    paraphrases = []

    for i in range(len(permutations)):
        code_shifts.append(', '.join(list(f'tree{"".join(map(lambda n: f"[{n}]", sh))}' for sh in permutations[i])))

    paraphrases.append(tree)
    for i in range(len(code_shifts) - 1):
        code = f'{code_shifts[0].replace("tree", "new_tree")} = {code_shifts[i + 1]}'
        exec(code)
        paraphrases.append(deepcopy(new_tree))
    
    if output == 'text':
        paraphrases = [' '.join(t.leaves()) for t in paraphrases]
    elif output == 'json':
        paraphrases = {'paraphrases': [{'tree': re.sub('\n\s+', ' ', str(t))} for t in paraphrases]}
        paraphrases = json.dumps(paraphrases)
    else:
        paraphrases = [re.sub('\n\s+', ' ', str(t)) for t in paraphrases]
    return paraphrases

if __name__ == "__main__":
    import doctest
    doctest.testmod()
