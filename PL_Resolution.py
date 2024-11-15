from itertools import combinations

class Clause:
    def __init__(self, literals=None):
        self.literals = set() if literals is None else set(literals)
    
    def __str__(self):
        if not self.literals:
            return "{}"
        return " OR ".join(sorted(self.literals, key=lambda x: x.replace('-', '')))
    
    def __eq__(self, other):
        return self.literals == other.literals
    
    def __hash__(self):
        return hash(frozenset(self.literals))

def parse_clause(clause_str):
    if not clause_str or clause_str == "{}":
        return Clause()
    literals = clause_str.split(" OR ")
    return Clause([lit.strip() for lit in literals])

def is_tautology(clause):
    literals = list(clause.literals)
    for lit in literals:
        if lit.startswith('-'):
            if lit[1:] in clause.literals:
                return True
        else:
            if f"-{lit}" in clause.literals:
                return True
    return False

def resolve(ci, cj):
    resolved_clauses = set()
    ci_lits = ci.literals
    cj_lits = cj.literals
    
    for lit_i in ci_lits:
        complement = f"-{lit_i}" if not lit_i.startswith('-') else lit_i[1:]
        if complement in cj_lits:
            new_literals = ci_lits.union(cj_lits) - {lit_i, complement}
            new_clause = Clause(new_literals)
            if not is_tautology(new_clause):
                resolved_clauses.add(new_clause)
                
    return resolved_clauses

def pl_resolution(kb, alpha):
    # Thêm phủ định của alpha vào KB
    clauses = kb.copy()
    clauses.update(negate_clause(alpha))
    
    # Tập hợp tất cả các mệnh đề đã có (bao gồm KB ban đầu)
    seen_clauses = clauses.copy()
    
    new_clauses_by_iteration = []
    iteration = 1
    
    while True:
        # Tập hợp các mệnh đề mới trong vòng lặp hiện tại
        new_clauses = set()
        
        # Thực hiện hợp giải trên tất cả các cặp mệnh đề hiện có
        pairs = list(combinations(clauses, 2))
        for ci, cj in pairs:
            resolvents = resolve(ci, cj)
            # Chỉ giữ lại các mệnh đề chưa xuất hiện trước đó
            new_clauses.update(resolvents - seen_clauses)
        
        # Kiểm tra điều kiện dừng
        if not new_clauses:  # Không có mệnh đề mới
            return new_clauses_by_iteration, False
            
        # Kiểm tra có mệnh đề rỗng không
        empty_clause = Clause()
        if empty_clause in new_clauses:
            new_clauses_by_iteration.append(["{}"])
            return new_clauses_by_iteration, True
        
        # Thêm các mệnh đề mới vào tập đã thấy và KB hiện tại
        seen_clauses.update(new_clauses)
        clauses.update(new_clauses)
        
        # Ghi nhận các mệnh đề mới của vòng lặp này (đã sắp xếp)
        sorted_new_clauses = sorted([str(clause) for clause in new_clauses])
        if sorted_new_clauses:
            new_clauses_by_iteration.append(sorted_new_clauses)
        
        iteration += 1

def negate_clause(clause):
    result = set()
    for literal in clause.literals:
        if literal.startswith('-'):
            result.add(Clause([literal[1:]]))
        else:
            result.add(Clause([f"-{literal}"]))
    return result

def read_input(filename):
    with open(filename, 'r') as f:
        alpha = parse_clause(f.readline().strip())
        n = int(f.readline().strip())
        kb = set()
        for _ in range(n):
            clause = parse_clause(f.readline().strip())
            if not is_tautology(clause):
                kb.add(clause)
    return kb, alpha

def write_output(filename, iteration_results, entails):
    with open(filename, 'w') as f:
        for results in iteration_results:
            f.write(f"{len(results)}\n")
            for clause in results:
                f.write(f"{clause}\n")
        f.write("YES\n" if entails else "NO\n")

def main():
    kb, alpha = read_input(".\input\input_02.txt")
    iteration_results, entails = pl_resolution(kb, alpha)
    write_output("output.txt", iteration_results, entails)

if __name__ == "__main__":
    main()