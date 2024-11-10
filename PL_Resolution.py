from typing import List, Set, Tuple
import itertools

class Clause:
    def __init__(self, literals: str = ""):
        # Chuyển đổi chuỗi input thành tập hợp các literal
        self.literals = set()
        if literals:
            if literals == "{}":  # Mệnh đề rỗng
                return
            parts = literals.split("OR")
            for part in parts:
                self.literals.add(part.strip())
    
    def __str__(self) -> str:
        if not self.literals:
            return "{}"
        # Sắp xếp các literal theo thứ tự chữ cái
        sorted_literals = sorted(self.literals, key=lambda x: (x.replace("-", ""), len(x)))
        return " OR ".join(sorted_literals)
    
    def __eq__(self, other) -> bool:
        return self.literals == other.literals
    
    def __hash__(self) -> int:
        return hash(frozenset(self.literals))

def negate_literal(literal: str) -> str:
    return literal[1:] if literal.startswith('-') else f'-{literal}'

def negate_clause(clause: str) -> List[str]:
    """Phủ định một mệnh đề (chuyển OR thành AND)"""
    literals = [lit.strip() for lit in clause.split("OR")]
    return [negate_literal(lit) for lit in literals]

def is_tautology(clause: Clause) -> bool:
    """Kiểm tra xem mệnh đề có phải là tautology không"""
    for lit in clause.literals:
        if negate_literal(lit) in clause.literals:
            return True
    return False

def is_contradiction(clause: Clause, clauses: Set[Clause]) -> bool:
    """Kiểm tra xem mệnh đề mới có mâu thuẫn với KB hiện tại không"""
    for existing_clause in clauses:
        if len(existing_clause.literals) == 1 and \
           len(clause.literals) == 1 and \
           list(existing_clause.literals)[0] == negate_literal(list(clause.literals)[0]):
            return True
    return False

def read_input(filename: str) -> Tuple[str, List[str]]:
    with open(filename, 'r') as f:
        alpha = f.readline().strip()
        n = int(f.readline().strip())
        kb = [f.readline().strip() for _ in range(n)]
    return alpha, kb

def write_output(filename: str, resolutions: List[List[Clause]], is_entailed: bool):
    with open(filename, 'w') as f:
        for round_clauses in resolutions:
            if round_clauses:  # Chỉ ghi các vòng có mệnh đề mới
                f.write(f"{len(round_clauses)}\n")
                for clause in round_clauses:
                    f.write(f"{str(clause)}\n")
        f.write("YES" if is_entailed else "NO")
        

def contradicts_kb(clause: Clause, kb: Set[Clause]) -> bool:
    # Kiểm tra xem clause có mâu thuẫn với mệnh đề nào trong KB không
    for existing in kb:
        if len(existing.literals) == 1:
            lit = list(existing.literals)[0]
            if any(l == negate_literal(lit) for l in clause.literals):
                return True
    return False


def pl_resolve(ci: Clause, cj: Clause, existing_clauses: Set[Clause]) -> Set[Clause]:
    resolvents = set()
    for li in ci.literals:
        for lj in cj.literals:
            if li == negate_literal(lj):
                # Tạo mệnh đề mới không chứa li và lj
                new_literals = (ci.literals | cj.literals) - {li, lj}
                new_clause = Clause()
                new_clause.literals = new_literals
                
                # Kiểm tra tính hợp lý của mệnh đề mới
                if not is_tautology(new_clause) and \
                   not contradicts_kb(new_clause, existing_clauses) and \
                   new_clause not in existing_clauses:
                    resolvents.add(new_clause)
    return resolvents

def pl_resolution(kb: List[str], alpha: str) -> Tuple[List[List[Clause]], bool]:
    # Khởi tạo KB với các mệnh đề ban đầu
    clauses = {Clause(c) for c in kb}
    
    # Thêm phủ định của alpha vào KB
    for neg_alpha in negate_clause(alpha):
        clauses.add(Clause(neg_alpha))
    
    resolutions = []  # Lưu các mệnh đề mới của mỗi vòng
    old_clauses = set()  # Tập các mệnh đề đã xét
    
    while True:
        # Tạo các cặp mệnh đề để hợp giải
        pairs = list(itertools.combinations(clauses, 2))
        new_clauses = set()
        
        for ci, cj in pairs:
            # Chỉ hợp giải các cặp mà ít nhất 1 mệnh đề chưa được xét
            if ci in old_clauses and cj in old_clauses:
                continue
                
            resolvents = pl_resolve(ci, cj, clauses)
            
            # Kiểm tra mệnh đề rỗng
            empty_clause = Clause()
            if empty_clause in resolvents:
                if new_clauses:  # Nếu đã có mệnh đề mới trong vòng này
                    resolutions.append(sorted(new_clauses, key=str))
                resolutions.append([empty_clause])  # Thêm mệnh đề rỗng vào vòng cuối
                return resolutions, True
            
            new_clauses.update(resolvents)
        
        # Nếu không còn mệnh đề mới
        if not new_clauses:
            return resolutions, False
        
        # Cập nhật các tập mệnh đề
        if new_clauses:
            resolutions.append(sorted(new_clauses, key=str))
        old_clauses.update(clauses)  # Lưu các mệnh đề đã xét
        clauses.update(new_clauses)  # Thêm mệnh đề mới vào KB

def main():
    input_file = "input.txt"
    output_file = "output.txt"
    
    # Đọc input
    alpha, kb = read_input(input_file)
    
    # Thực hiện hợp giải
    resolutions, is_entailed = pl_resolution(kb, alpha)
    
    # Ghi output
    write_output(output_file, resolutions, is_entailed)

if __name__ == "__main__":
    main()