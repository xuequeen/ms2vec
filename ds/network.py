#!/usr/bin/python
# -*- encoding: utf8 -*-

import cPickle
import random
import numpy as np


__author__ = 'sheep'


class HIN(object):
    '''
        a heterogeneous information network
        which support multigraph, weighted edges
    '''
    def __init__(self):
        self.graph = {} #{from_id: {to_id: {edge_class_id: weight}}}
        #TODO correct the name
        self.class_nodes = {} #{node_class: set([node_id])}
        self.edge_class2id = {} #{edge_class: edge_class_id}
        self.node2id = {} #{node: node_id}
        self.edge_class_id_available_node_class = {} # {edge_class_id:
                                                     #  (from_node_class, to_node_class)}

    def __eq__(self, other):
        if not isinstance(other, HIN):
            return False
        if self.graph != other.graph:
            return False
        if self.class_nodes != other.class_nodes:
            return False
        if self.edge_class2id != other.edge_class2id:
            return False
        if self.node2id != other.node2id:
            return False
        if self.edge_class_id_available_node_class != other.edge_class_id_available_node_class:
            return False
        return True

    def node_count(self):
        return len(self.graph)

    def edge_count(self):
        count = 0
        for from_id in self.graph:
            for to_ids in self.graph[from_id].values():
                count += len(to_ids)
        return count

    def dump_to_file(self, fname):
        with open(fname, 'w') as f:
            cPickle.dump(self, f)

    @staticmethod
    def load_from_file(fname):
        with open(fname, 'r') as f:
            return cPickle.load(f)

    @staticmethod
    def load_from_edge_file(fname):
        g = HIN()
        with open(fname, 'r') as f:
            for line in f:
                line = line.strip()
                tokens = line.split()
                g.add_edge(tokens[0], '', tokens[1], '', '',
                           weight=int(tokens[2]))
                g.add_edge(tokens[1], '', tokens[0], '', '',
                           weight=int(tokens[2]))
        return g

    @staticmethod
    #FIXME
    def get_inverse_edge(edge):
        inversed = edge[::-1]
        if '>' in inversed:
            inversed = inversed.replace('>', '<')
        elif '<' in inversed:
            inversed = inversed.replace('<', '>')
        return inversed

    #FIXME
    def get_edge_class_inverse_mappling(self):
        inverse_mapping = {}
        for edge_class in self.edge_class2id.keys():
            inversed = edge_class[::-1]
            if '>' in inversed:
                inversed = inversed.replace('>', '<')
            elif '<' in inversed:
                inversed = inversed.replace('<', '>')
            if inversed != edge_class and inversed in self.edge_class2id:
                inverse_mapping[str(self.edge_class2id[edge_class])] = str(self.edge_class2id[inversed])
        return inverse_mapping

    def add_edge(self, from_node, from_class, to_node, to_class,edge_class,
                 weight = 1):
        if edge_class not in self.edge_class2id:
            self.edge_class2id[edge_class] = len(self.edge_class2id)
        edge_id = self.edge_class2id[edge_class]

        if edge_id not in self.edge_class_id_available_node_class:
            self.edge_class_id_available_node_class[edge_id] = (from_class, to_class)

        if from_node not in self.node2id:
            self.node2id[from_node] = len(self.node2id)
        from_id = self.node2id[from_node]
        if to_node not in self.node2id:
            self.node2id[to_node] = len(self.node2id)
        to_id = self.node2id[to_node]

        if from_class not in self.class_nodes:
            self.class_nodes[from_class] = set()
        self.class_nodes[from_class].add(from_id)

        if to_class not in self.class_nodes:
            self.class_nodes[to_class] = set()
        self.class_nodes[to_class].add(to_id)

        if from_id not in self.graph:
            self.graph[from_id] = {to_id: {edge_id: weight}}
            return
        if to_id not in self.graph[from_id]:
            self.graph[from_id][to_id] = {edge_id: weight}
            return
        self.graph[from_id][to_id][edge_id] = weight

    def has_node(self, node):
        return node in self.node2id

    def has_edge(self, from_node, to_node, edge_class=None):
        if from_node not in self.node2id:
            return False
        if to_node not in self.node2id:
            return False
        if edge_class is not None:
            edge_class_id = self.edge_class2id[edge_class]
            from_id = self.node2id[from_node]
            to_id = self.node2id[to_node]
            if to_id in self.graph[from_id][edge_class_id]:
                return True
            return False
        else:
            from_id = self.node2id[from_node]
            to_id = self.node2id[to_node]
            for to_ids in self.graph[from_id].values():
                if to_id in to_ids:
                    return True
            return False

    def common_neighbors(self, from_id, to_id):
        from_neighbors = set(self.graph[from_id][0].keys())
        to_neighbors = set(self.graph[to_id][0].keys())
        return from_neighbors.intersection(to_neighbors)

    def ratio_common_neighbors(self, from_id, to_id):
        from_neighbors = set(self.graph[from_id][0].keys())
        to_neighbors = set(self.graph[to_id][0].keys())
        intersection = from_neighbors.intersection(to_neighbors)
        union = from_neighbors.union(to_neighbors)
        return float(len(intersection))/len(union)

    def update_ids(self, id2new):
        graph = {}
        for from_ in self.graph:
            graph[id2new[from_]] = {}
            for to_, adict in self.graph[from_].items():
                graph[id2new[from_]][id2new[to_]] = adict
        self.graph = graph

        for class_ in self.class_nodes:
            aset = set()
            for id_ in self.class_nodes[class_]:
                aset.add(id2new[id_])
            self.class_nodes[class_] = aset

        for node in self.node2id:
            self.node2id[node] = id2new[self.node2id[node]]

    def print_statistics(self):
        for c, nodes in self.class_nodes.items():
            print c, len(nodes)
        class_count = {}
        for class_edges in self.graph.values():
            for class_, to_ids in class_edges.items():
                if class_ not in class_count:
                    class_count[class_] = len(to_ids)
                    continue
                class_count[class_] += len(to_ids)
        print self.edge_class2id
        for class_, count in class_count.items():
            print class_, count

    def to_homogeneous_network(self):
        aset = set()
        for nodes in self.class_nodes.values():
            aset.update(nodes)
        self.class_nodes = {'': aset}

        self.edge_class2id = {'': 0}

        self.edge_class_id_available_node_class = {}

        graph = {}
        for from_id, to_edges in self.graph.items():
            graph[from_id] = {}
            for to_id, edges in to_edges.items():
                weight = sum(edges.values())
                graph[from_id][to_id] = {0: weight}
        self.graph = graph

    #TODO support multigraph
    #TODO speed up
    def to_weighted_edge_list(self, with_edge_class_id=False):
        '''
            ignore edge type
        '''
        id2node = dict([(v, k) for k, v in self.node2id.items()])
        edges = []
        for node_id in self.graph:
            for to_id, to_edges in self.graph[node_id].items():
                for edge_class_id, weight in to_edges.items():
                    if with_edge_class_id:
                        edge = (id2node[node_id],
                                id2node[to_id],
                                weight,
                                edge_class_id)
                    else:
                        edge = (id2node[node_id], id2node[to_id], weight)
                    edges.append(edge)
        return edges

    def dump_edge_list_file(self, fname):
        node2class = {}
        for c, ids in self.class_nodes.items():
            for id_ in ids:
                node2class[id_] = c

        edge_class_id2edge_class = {}
        for c, id_ in self.edge_class2id.items():
            edge_class_id2edge_class[id_] = c

        with open(fname, 'w') as f:
            for node_id in self.graph:
                for edge_class_id, tos in self.graph[node_id].items():
                    for to_id, weight in tos.items():
                        line = ('%d\t%d\t%f\t%s\t%s\t%s\n'
                                '' % (node_id,
                                  to_id,
                                  weight,
                                  node2class[node_id],
                                  node2class[to_id],
                                  edge_class_id2edge_class[edge_class_id]))
                        f.write(line)

    def get_ids(self):
        return sorted(self.node2id.values())

    def a_random_walk(self, node, length):
        if node not in self.graph:
            return []
        if not hasattr(self, 'node_choices'):
            self.create_node_choices()

        walk = [node]
        length -= 1
        while length > 0:
            if len(self.graph[node]) == 0:
                return walk

            next_node, edge_class_id =random.choice(self.node_choices[node])

            walk.append(next_node)
            node = next_node
            length -= 1
        return walk

    def create_node_choices(self):
        node_choices = {} #{from_id: [(to_id, edge_class_id)]} 
        for from_id in self.graph:
            node_choices[from_id] = []
            for to_id in self.graph[from_id]:
                for edge_id, w in self.graph[from_id][to_id].items():
                    node_choices[from_id] += [(to_id, edge_id)] * int(w*10)
        self.node_choices = node_choices

    def random_walks(self, count, length, seed=None):
        '''
            Generate random walks starting from each node

            input:
                count: the # of random walks starting from each node
                length: the maximam length of a random walk

            output:
                [random_walk]
                    random_walk: [<node_id>,<edge_class_id>,<node_id>, ...]
        '''

        random.seed(seed)
        np.random.seed(seed)

        if not hasattr(self, 'node_choices'):
            self.create_node_choices()

        for c in range(count):
#           print c
            n = 0
            for node in self.graph:
                n += 1
                if n % 10000 == 0:
                    print n
                walk = self.a_random_walk(node, length)
                if len(walk) != 1:
                    yield walk

    def random_remove_edges(self, edge_class, ratio=0.5, seed=None):
        random.seed(seed)
        edge_class_id = self.edge_class2id[edge_class]
        inv_edge_class_mapping = self.get_edge_class_inverse_mappling()
        try:
            inv_edge_class_id = int(inv_edge_class_mapping[str(edge_class_id)])
        except:
            inv_edge_class_id = edge_class_id

        edges = []
        for from_id, tos in self.graph.items():
            for to_id, to_edges in tos.items():
                if edge_class_id not in to_edges:
                    continue
                edges.append((from_id, to_id))
        random.shuffle(edges)
        for from_id, to_id in edges[:int(len(edges)*ratio)]:
            try:
                self.graph[from_id][to_id].pop(edge_class_id)
                if len(self.graph[from_id][to_id]) == 0:
                    self.graph[from_id].pop(to_id)
                self.graph[to_id][from_id].pop(inv_edge_class_id)
                if len(self.graph[to_id][from_id]) == 0:
                    self.graph[to_id].pop(from_id)
            except:
                continue
        return edges[:int(len(edges)*ratio)]

    def random_select_neg_edges(self, edge_class, count, seed=None):
        random.seed(seed)
        edge_class_id = self.edge_class2id[edge_class]
        from_class, to_class = self.edge_class_id_available_node_class[edge_class_id]
        from_ids = list(self.class_nodes[from_class])
        from_id_size = len(from_ids)
        to_ids = list(self.class_nodes[to_class])
        to_id_size = len(to_ids)
        selected = set()
        while len(selected) < count:
            rand_from_id = from_ids[random.randint(0, from_id_size-1)]
            rand_to_id = to_ids[random.randint(0, to_id_size-1)]
            if (rand_from_id, rand_to_id) in selected:
                continue
            if (rand_to_id in self.graph[rand_from_id]
                and edge_class_id in self.graph[rand_from_id][rand_to_id]):
                continue
            selected.add((rand_from_id, rand_to_id))
            if len(selected) % 10000 == 0:
                print len(selected)
        return selected

    def to_edge_class_id_string(self, edge_classes):
        return ','.join(map(str, [self.edge_class2id[ec] for ec in edge_classes]))


class Node(object):
    '''
        Node for Nodes
    '''
    def __init__(self, node_id, count=0):
        self.node_id = node_id
        self.count = count

    def __str__(self):
        return '%s(%d)' % (self.node_id, self.count)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        if self.node_id != other.node_id:
            return False
        if self.count != other.count:
            return False
        return True


class NodeVocab(object):

    def __init__(self):
        self.nodes = []
        self.node2index = {}
        self.node_count = 0

    def add_node(self, node_id):
        self.node2index[node_id] = len(self.nodes)
        self.nodes.append(Node(node_id))
        self.node_count += 1

    @staticmethod
    def load_from_network(g):
        nodes = []
        node2index = {}
        node_count = len(g.graph)

        for id_ in g.graph:
            degree = 0
            for to_ids in g.graph[id_].values():
                degree += len(to_ids)

            id_string = str(id_)
            node2index[id_string] = len(nodes)
            node = Node(id_string)
            node.count = degree
            nodes.append(node)

        node_vocab = NodeVocab()
        node_vocab.nodes = nodes
        node_vocab.node2index = node2index
        node_vocab.node_count = node_count
        node_vocab._sort()
        return node_vocab

    @staticmethod
    def load_from_file(fname, available_ids=None):
        '''
            input:
                training_fname:
                    each line: <node_id> <edge_id> ...
                available_ids: set([<node_id>])
                    node_id should be a string
        '''
        with open(fname, 'r') as f:
            nodes = []
            node2index = {}
            node_count = 0

            for line in f:
                tokens = line.strip().split()
                for i, token in enumerate(tokens):
                    if i % 2 == 1:
                        continue
                    if available_ids is not None and token not in available_ids:
                        continue

                    if token not in node2index:
                        node2index[token] = len(nodes)
                        nodes.append(Node(token))

                    nodes[node2index[token]].count += 1
                    node_count += 1

                    if node_count % 10000 == 0:
                        sys.stdout.write("\rReading nodes %d" % node_count)
                        sys.stdout.flush()
            print

            node_vocab = NodeVocab()
            node_vocab.nodes = nodes
            node_vocab.node2index = node2index
            node_vocab.node_count = node_count
            node_vocab._sort()
            return node_vocab

    def __getitem__(self, i):
        return self.nodes[i]

    def __len__(self):
        return len(self.nodes)

    def __contains__(self, key):
        return key in self.node2index

    def __str__(self):
        return ('Node vocab size: %d\nTotal nodes: %d'
                '' % (len(self), self.node_count))

    def __eq__(self, other):
        if not isinstance(other, NodeVocab):
            return False
        if self.nodes != other.nodes:
            return False
        if self.node_count != other.node_count:
            return False
        if self.node2index != other.node2index:
            return False
        return True

    def _sort(self):
        self.nodes.sort(key=lambda x: x.count, reverse=True)
        node2index = {}
        for i, node in enumerate(self.nodes):
            node2index[node.node_id] = i
        self.node2index = node2index

    def count(self):
        return self.node_count

    def to_indices(self, node_ids):
        return [self.node2index[id_] for id_ in node_ids]


class Path(object):
    '''
        Path for PathVocab
    '''
    def __init__(self, path_id, count=0, is_inverse=False):
        self.path_id = path_id
        self.count = count
        self.is_inverse = is_inverse

    def __str__(self):
        return '%s(count:%d, inverse:%s)' % (self.path_id, self.count, self.is_inverse)

    def __eq__(self, other):
        if not isinstance(other, Path):
            return False
        if self.path_id != other.path_id:
            return False
        if self.count != other.count:
            return False
        if self.is_inverse != other.is_inverse:
            return False
        return True


class PathVocab(object):
    '''
        a path is a list of edges
    '''

    def __init__(self):
        self.paths = []
        self.path2index = {}
        self.path_count = 0

    def add_path(self, path_id):
        self.path2index[path_id] = len(self.paths)
        self.paths.append(Path(path_id))
        self.path_count += 1

    @staticmethod
    #TODO the order of edges of the path
    def load_from_file(fname, window_size, inverse_mapping=None):
        '''
            input:
                training_fname:
                    each line: <node_id> <edge_id> ...
                window_size: the maximal window size for paths
        '''
        def inverse_edges(edges, inverse_mapping):
            return [inverse_mapping.get(e, e) for e in edges[::-1]]

        with open(fname, 'r') as f:
            paths = []
            path2index = {}
            path_count = 0

            for line in f:
                tokens = line.strip().split()
                tokens = [t for i, t in enumerate(tokens) if i % 2 == 1]
                for w in range(window_size):
                    for i in range(len(tokens)-w):
                        edges = tokens[i:i+1+w]
                        path = ','.join(edges)
                        if path not in path2index:

                            if inverse_mapping is not None:
                                inverse_path = ','.join(inverse_edges(edges, inverse_mapping))
                                if inverse_path not in path2index:
                                    path2index[path] = len(paths)
                                    paths.append(Path(path))
                                else:
                                    path2index[path] = path2index[inverse_path]
                                    paths.append(Path(path, is_inverse=True))
                            else:
                                path2index[path] = len(paths)
                                paths.append(Path(path))

                        paths[path2index[path]].count += 1
                        path_count += 1

                        if path_count % 10000 == 0:
                            sys.stdout.write("\rReading paths %d"
                                             "" % path_count)
                            sys.stdout.flush()
            print

            path_vocab = PathVocab()
            path_vocab.paths = paths
            path_vocab.path2index = path2index
            path_vocab.path_count = path_count
            path_vocab._sort()
            return path_vocab

    def __getitem__(self, i):
        return self.paths[i]

#   def __len__(self):
#       return len(self.paths)

    def distinct_path_count(self):
        return max(self.path2index.values())+1

    def count(self):
        return self.path_count

    def __contains__(self, key):
        return key in self.path2index

    def __str__(self):
        return ('Path vocab size: %d\nTotal paths: %d'
                '' % (len(self), self.node_count))

    def __eq__(self, other):
        if not isinstance(other, PathVocab):
            return False
        if self.paths != other.paths:
            return False
        if self.path_count != other.path_count:
            return False
        if self.path2index != other.path2index:
            return False
        return True

    def _sort(self):
        old_paths = copy.deepcopy(self.paths)
        self.paths.sort(key=lambda x: x.count, reverse=True)
        path2index = {}
        for i, path in enumerate(self.paths):
            if path.is_inverse:
                index = path2index[old_paths[self.path2index[path.path_id]].path_id]
#               print path, self.path2index[path.path_id], index
            else:
                index = i
            path2index[path.path_id] = index
        self.path2index = path2index

    def to_indices(self, path_ids):
        return [self.path2index[id_] for id_ in path_ids]


class EdgeNodePathVocab(PathVocab):
    '''
        a path is: <edge> <node> <edge> ...
    '''
    @staticmethod
    #TODO the order of edges of the path
    def load_from_file(fname, window_size):
        '''
            input:
                training_fname:
                    each line: <node_id> <edge_id> ...
                window_size: the maximal window size for paths
        '''
        with open(fname, 'r') as f:
            paths = []
            path2index = {}
            path_count = 0

            for line in f:
                tokens = line.strip().split()
#               tokens = [t for i, t in enumerate(tokens) if i % 2 == 1]
                for w in range(window_size):
                    for i in range(1, len(tokens)-w*2, 2):
                        path = ','.join(tokens[i:i+1+w*2])
                        if path not in path2index:
                            path2index[path] = len(paths)
                            paths.append(Path(path))

                        paths[path2index[path]].count += 1
                        path_count += 1

                        if path_count % 10000 == 0:
                            sys.stdout.write("\rReading paths %d"
                                             "" % path_count)
                            sys.stdout.flush()
            print

            path_vocab = EdgeNodePathVocab()
            path_vocab.paths = paths
            path_vocab.path2index = path2index
            path_vocab.path_count = path_count
            path_vocab._sort()
            return path_vocab

    def __str__(self):
        return ('EdgeNodePath vocab size: %d\nTotal paths: %d'
                '' % (len(self), self.node_count))

    def __eq__(self, other):
        if not isinstance(other, EdgeNodePathVocab):
            return False
        if self.paths != other.paths:
            return False
        if self.path_count != other.path_count:
            return False
        if self.path2index != other.path2index:
            return False
        return True
