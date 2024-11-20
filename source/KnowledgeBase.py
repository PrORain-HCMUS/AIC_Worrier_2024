import itertools

class KnowledgeBase:
    def __init__(self):
        # Khởi tạo cơ sở dữ liệu để lưu các mệnh đề
        self.database = []
        # Lưu lại đường đi của quá trình hợp giải
        self.resolution_path = []

    def insert(self, statement):
        # Thêm một mệnh đề mới vào cơ sở dữ liệu nếu nó chưa tồn tại và không mâu thuẫn
        if statement not in self.database and not self.has_contradiction(statement):
            self.database.append(statement)

    def invert_literal(self, literal):
        # Đảo ngược một literal (thêm hoặc bỏ dấu -)
        if (literal[0] == '-'):
            return literal[1:]
        else:
            return '-' + literal

    def invert_expression(self, expression):
        # Phủ định một biểu thức logic
        result = []
        for statement in expression:
            temp = []
            for literal in statement:
                temp.append([self.invert_literal(literal)])
            result.append(temp)
        
        # Nếu chỉ có một mệnh đề, trả về dạng phẳng
        if len(result) == 1:
            return list(itertools.chain.from_iterable(result))
        else:
            return self.convert_to_standard_form(result)

    def is_subset_exists(self, statement, statement_list):
        # Kiểm tra xem một mệnh đề có là tập con của bất kỳ mệnh đề nào trong danh sách không
        for existing in statement_list:
            if set(existing).issubset(set(statement)):
                return True
        return False

    def eliminate_redundant(self, statements):
        # Loại bỏ các mệnh đề dư thừa
        output = []
        for stmt in statements:
            if not self.is_subset_exists(stmt, output):
                output.append(stmt)
        return output

    def convert_to_standard_form(self, statements):
        # Chuyển đổi các mệnh đề về dạng chuẩn CNF
        output = []
        # Tạo tất cả các tổ hợp có thể từ các mệnh đề
        combinations = list(itertools.product(*statements))
        for combo in combinations:
            processed = self.standardize_statement(list(itertools.chain.from_iterable(list(combo))))
            if not self.has_contradiction(processed) and processed not in output:
                output.append(processed)
        output.sort(key=len)
        output = self.eliminate_redundant(output)
        return output

    def has_contradiction(self, statement):
        # Kiểm tra xem một mệnh đề có mâu thuẫn nội tại không
        for literal in statement:
            if self.invert_literal(literal) in statement:
                return True
        return False

    def standardize_statement(self, statement):
        # Chuẩn hóa một mệnh đề bằng cách loại bỏ trùng lặp và sắp xếp
        # Loại bỏ các literal trùng lặp
        unique_literals = list(dict.fromkeys(statement))
        
        # Chuyển đổi sang dạng tuple để sắp xếp
        formatted_literals = []
        for literal in unique_literals:
            if literal[0] == '-':
                formatted_literals.append((literal[1], -1))
            else:
                formatted_literals.append((literal[0], 1))
        formatted_literals.sort()
        
        # Chuyển đổi lại về dạng chuỗi
        result = []
        for item in formatted_literals:
            if item[1] == -1:
                result.append('-' + item[0])
            else:
                result.append(item[0])
        return result

    def apply_resolution(self, stmt1, stmt2):
        # Áp dụng quy tắc hợp giải trên hai mệnh đề
        derived_statements = []
        for literal in stmt1:
            opposite = self.invert_literal(literal)
            if opposite in stmt2:
                # Tạo bản sao để không ảnh hưởng đến mệnh đề gốc
                temp_stmt1 = stmt1.copy()
                temp_stmt2 = stmt2.copy()
                # Loại bỏ cặp literal đối ngẫu
                temp_stmt1.remove(literal)
                temp_stmt2.remove(opposite)
                if not temp_stmt1 and not temp_stmt2:
                    derived_statements.append(['{}'])
                else:
                    combined = temp_stmt1 + temp_stmt2
                    standardized = self.standardize_statement(combined)
                    if not self.has_contradiction(standardized) and standardized not in self.database:
                        derived_statements.append(standardized)
        return derived_statements

    def prove_by_resolution(self, target):
        # Phương pháp chứng minh bằng hợp giải
        # Tạo một bản sao tạm thời của cơ sở tri thức
        temp_kb = KnowledgeBase()
        temp_kb.database = self.database.copy()

        # Phủ định mệnh đề cần chứng minh
        negated_target = self.invert_expression(target)
        print(f"Mệnh đề phủ định: {negated_target}")
        for neg_stmt in negated_target:
            temp_kb.insert(neg_stmt)
        
        proof_steps = []
        step_counter = 1
        while True:
            # Tạo tất cả các cặp mệnh đề có thể
            statement_pairs = list(itertools.combinations(range(len(temp_kb.database)), 2))
            
            # Lưu các mệnh đề mới được sinh ra từ hợp giải
            new_statements = []
            for pair in statement_pairs:
                resolvent = temp_kb.apply_resolution(temp_kb.database[pair[0]], temp_kb.database[pair[1]])
                if resolvent and resolvent not in new_statements:
                    new_statements.append(resolvent)
                    # Lưu lại các bước hợp giải
                    self.resolution_path.append((temp_kb.database[pair[0]], temp_kb.database[pair[1]], resolvent))
                    print(f"Bước {step_counter}: Hợp giải {temp_kb.database[pair[0]]} và {temp_kb.database[pair[1]]} -> {resolvent}")
                    step_counter += 1

                    if ['{}'] in resolvent:
                        return proof_steps, True

            # Làm phẳng danh sách các mệnh đề mới
            new_statements = list(itertools.chain.from_iterable(new_statements))
            proof_steps.append(new_statements)


            # Nếu không có mệnh đề mới nào được tạo ra
            if not new_statements:
                return proof_steps, False
            else:
                # Nếu tìm thấy mệnh đề rỗng, chứng minh thành công
                if ['{}'] in new_statements:
                    return proof_steps, True
                else:
                    # Thêm các mệnh đề mới vào cơ sở tri thức
                    for res in new_statements:
                        temp_kb.insert(res)