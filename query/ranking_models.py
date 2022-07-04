from typing import List
from abc import abstractmethod
from typing import List, Set,Mapping
from index.structure import TermOccurrence
import math
from enum import Enum

class IndexPreComputedVals():
    def __init__(self,index):
        self.index = index
        self.precompute_vals()

    def precompute_vals(self):
        """
        Inicializa os atributos por meio do indice (idx):
            doc_count: o numero de documentos que o indice possui
            document_norm: A norma por documento (cada termo é presentado pelo seu peso (tfxidf))
        """
        self.document_norm = {}
        self.doc_count = self.index.document_count       

        tf_idf_dict = dict()

        for term in self.index.dic_index:          
            for occurrence in self.index.get_occurrence_list(term): 
                if occurrence.doc_id in tf_idf_dict.keys():
                    tf_idf_dict[occurrence.doc_id].append(VectorRankingModel.tf_idf(self.doc_count, occurrence.term_freq, self.index.dic_index[term].doc_count_with_term))
                else:
                    tf_idf_dict[occurrence.doc_id] = [VectorRankingModel.tf_idf(self.doc_count, occurrence.term_freq, self.index.dic_index[term].doc_count_with_term)]

        for doc_id, values in tf_idf_dict.items():
            sum = 0
            for tf_idf in values:
                sum += tf_idf**2
            self.document_norm[doc_id] = math.sqrt(sum)

class RankingModel():
    @abstractmethod
    def get_ordered_docs(self,query:Mapping[str,TermOccurrence],
                              docs_occur_per_term:Mapping[str,List[TermOccurrence]]) -> (List[int], Mapping[int,float]):
        raise NotImplementedError("Voce deve criar uma subclasse e a mesma deve sobrepor este método")

    def rank_document_ids(self,documents_weight):
        doc_ids = list(documents_weight.keys())
        doc_ids.sort(key= lambda x:-documents_weight[x])
        return doc_ids

class OPERATOR(Enum):
  AND = 1
  OR = 2
    
#Atividade 1
class BooleanRankingModel(RankingModel):
    def __init__(self,operator:OPERATOR):
        self.operator = operator

    def intersection_all(self, map_lst_occurrences:Mapping[str,List[TermOccurrence]]) -> List[int]:
        
        set_lst = []

        for  term, lst_occurrences in map_lst_occurrences.items():
            set_ids = set()
            for term_occurence in lst_occurrences:
                set_ids.add(term_occurence.doc_id)
            set_lst.append(set_ids)    
                
        return set.intersection(*set_lst) if set_lst else set()

    def union_all(self, map_lst_occurrences:Mapping[str,List[TermOccurrence]]) -> List[int]:
        set_ids = set()
        
        for  term, lst_occurrences in map_lst_occurrences.items():
            for term_occurence in lst_occurrences:
                set_ids.add(term_occurence.doc_id)

        return set_ids

    def get_ordered_docs(self,query:Mapping[str,TermOccurrence],
                              map_lst_occurrences:Mapping[str,List[TermOccurrence]]) -> (List[int], Mapping[int,float]):
        """Considere que map_lst_occurrences possui as ocorrencias apenas dos termos que existem na consulta"""
        if self.operator == OPERATOR.AND:
            return self.intersection_all(map_lst_occurrences),None
        else:
            return self.union_all(map_lst_occurrences),None

#Atividade 2
class VectorRankingModel(RankingModel):

    def __init__(self,idx_pre_comp_vals:IndexPreComputedVals):
        self.idx_pre_comp_vals = idx_pre_comp_vals

    @staticmethod
    def tf(freq_term:int) -> float:
        return 1 + math.log2(freq_term)

    @staticmethod
    def idf(doc_count:int, num_docs_with_term:int )->float:
        return math.log2(doc_count/num_docs_with_term)

    @staticmethod
    def tf_idf(doc_count:int, freq_term:int, num_docs_with_term) -> float:
        tf = VectorRankingModel.tf(freq_term)
        idf = VectorRankingModel.idf(doc_count, num_docs_with_term)
        #print(f"TF:{tf} IDF:{idf} n_i: {num_docs_with_term} N: {doc_count}")
        return tf*idf

    def get_ordered_docs(self,query:Mapping[str,TermOccurrence],
                              docs_occur_per_term:Mapping[str,List[TermOccurrence]]) -> (List[int], Mapping[int,float]):
            documents_weight = {}





            #retona a lista de doc ids ordenados de acordo com o TF IDF
            return self.rank_document_ids(documents_weight),documents_weight

