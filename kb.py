import itertools

class KnowledgeBase:
    def __init__(self):
        self.clauses = []
        self.steps = []  # Thêm thuộc tính steps để lưu trữ các bước hợp giải

    def addClause(self, clause):
        if clause not in self.clauses and not self.checkComplementary(clause):
            self.clauses.append(clause)

    def getNegative_atom(self, atom):
        if (atom[0] == '-'):
            return atom[1:]
        else:
            return '-' + atom

    def getNegative_query(self, query):
        res = []
        for clause in query:
            new = []
            for atom in clause:
                new.append([self.getNegative_atom(atom)])
            res.append(new)
        
        if len(res) == 1:
            return list(itertools.chain.from_iterable(res))
        else:
            return self.toCNF(res)

    def check_True(self, clause, list_clauses):
        for c in list_clauses:
            if set(c).issubset(set(clause)):
                return True
        return False

    def remove_eval(self, clauses):
        res = []
        for c in clauses:
            if not self.check_True(c, res):
                res.append(c)
        return res

    def toCNF(self, clauses):
        res = []
        product_all = list(itertools.product(*clauses))
        for i in product_all:
            new = self.normClause(list(itertools.chain.from_iterable(list(i))))
            if not self.checkComplementary(new) and new not in res:
                res.append(new)
        res.sort(key=len)
        res = self.remove_eval(res)
        return res

    def checkComplementary(self, clause):
        for atom in clause:
            if self.getNegative_atom(atom) in clause:
                return True
        return False

    def normClause(self, clause):
        # Remove duplicates
        clause = list(dict.fromkeys(clause))

        # Sort by alphabet
        tuple_form = []
        for atom in clause:
            if atom[0] == '-':
                tuple_form.append((atom[1], -1))
            else:
                tuple_form.append((atom[0], 1))
        tuple_form.sort()

        # Rebuild clause
        res = []
        for tup in tuple_form:
            if tup[1] == -1:
                res.append('-' + tup[0])
            else:
                res.append(tup[0])
        return res

    def resolve(self, clause_i, clause_j):
        new_clause = []
        for atom in clause_i:
            neg_atom = self.getNegative_atom(atom)
            if neg_atom in clause_j:
                temp_c_i = clause_i.copy()
                temp_c_j = clause_j.copy()
                temp_c_i.remove(atom)
                temp_c_j.remove(neg_atom)
                if not temp_c_i and not temp_c_j:
                    new_clause.append(['{}'])
                else:
                    clause = temp_c_i + temp_c_j
                    clause = self.normClause(clause)
                    if not self.checkComplementary(clause) and clause not in self.clauses:
                        new_clause.append(clause)
        return new_clause

    def PL_Resolution(self, query):
        tempKB = KnowledgeBase()
        tempKB.clauses = self.clauses.copy()

        neg_query = self.getNegative_query(query)
        print(f"Negative query: {neg_query}")
        for neg_atom in neg_query:
            tempKB.addClause(neg_atom)
        
        result = []
        step = 1
        while True:
            clause_pairs = list(itertools.combinations(range(len(tempKB.clauses)), 2))
            
            resolvents = []
            for pair in clause_pairs:
                resolvent = tempKB.resolve(tempKB.clauses[pair[0]], tempKB.clauses[pair[1]])
                if resolvent and resolvent not in resolvents:
                    resolvents.append(resolvent)
                    self.steps.append((tempKB.clauses[pair[0]], tempKB.clauses[pair[1]], resolvent))  # Lưu trữ các bước hợp giải
                    print(f"Step {step}: Resolving {tempKB.clauses[pair[0]]} and {tempKB.clauses[pair[1]]} -> {resolvent}")
                    step += 1

            resolvents = list(itertools.chain.from_iterable(resolvents))
            result.append(resolvents)

            if not resolvents:
                return result, False
            else:
                if ['{}'] in resolvents:
                    return result, True
                else:
                    for res in resolvents:
                        tempKB.addClause(res)
