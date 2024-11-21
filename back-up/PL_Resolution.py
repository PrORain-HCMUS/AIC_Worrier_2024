import os
import KnowledgeBase as kb
import re
import time
from typing import Tuple, List


class LogicResolver:
    def __init__(self, input_dir: str = './input/', output_dir: str = './output/'):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def _parse_input_file(self, content: List[str]) -> Tuple[kb.KnowledgeBase, List[List[str]]]:
        """
        Phân tích nội dung file input và khởi tạo Knowledge Base
        """
        # Lấy chữ cái cần query từ dòng đầu
        query_letter = content[0]
        
        # Tạo query dạng list of lists
        query = [[query_letter]]
        
        # Khởi tạo Knowledge Base
        knowledge_base = kb.KnowledgeBase()
        
        # Xử lý các mệnh đề từ dòng thứ 3 trở đi
        for cnf in content[2:]:
            # Tách các thành phần và loại bỏ 'OR'
            clause = [x for x in cnf.split() if x != 'OR']
            knowledge_base.insert(clause)

        return knowledge_base, query

    def _read_file(self, filepath: str) -> Tuple[kb.KnowledgeBase, List[List[str]]]:
        """
        Đọc và xử lý file input
        """
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                # Đọc và loại bỏ dòng trống
                content = [line.strip() for line in f.read().splitlines() if line.strip()]
                return self._parse_input_file(content)
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file {filepath}: {str(e)}")

    def _write_result(self, result: List[List[str]], is_proved: bool, filepath: str) -> None:
        """
        Ghi kết quả ra file output
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Ghi từng bước hợp giải
                for step_results in result:
                    # Ghi số lượng mệnh đề trong bước
                    f.write(f"{len(step_results)}\n")
                    
                    # Ghi từng mệnh đề
                    for clause in step_results:
                        clause_str = ' OR '.join(clause)
                        f.write(f"{clause_str}\n")
                    
                # Ghi kết quả cuối cùng
                f.write('YES' if is_proved else 'NO')
        except Exception as e:
            raise Exception(f"Lỗi khi ghi file {filepath}: {str(e)}")

    def _get_sorted_input_files(self) -> List[str]:
        """
        Lấy danh sách file input đã sắp xếp
        """
        try:
            files = [f for f in os.listdir(self.input_dir) 
                    if f.startswith('input_') and f.endswith('.txt')]
            return sorted(files, key=lambda x: int(re.search(r'input_(\d+)\.txt', x).group(1)))
        except Exception as e:
            raise Exception(f"Lỗi khi đọc thư mục input: {str(e)}")

    def _generate_output_filename(self, input_filename: str) -> str:
        """
        Tạo tên file output tương ứng với file input
        """
        match = re.search(r'input_(\d+)\.txt', input_filename)
        if not match:
            raise ValueError(f"Tên file không đúng định dạng: {input_filename}")
        return f'output_{match.group(1)}.txt'

    def process_single_file(self, input_filename: str) -> None:
        """
        Xử lý một file input đơn lẻ và đo thời gian xử lý
        """
        try:
            # Đường dẫn đầy đủ cho input và output
            input_path = os.path.join(self.input_dir, input_filename)
            output_path = os.path.join(self.output_dir, self._generate_output_filename(input_filename))

            # Bắt đầu tính thời gian
            start_time = time.time()

            # Đọc và xử lý file
            knowledge_base, query = self._read_file(input_path)
            
            # Thực hiện hợp giải
            result, is_proved = knowledge_base.prove_by_resolution(query)
            
            # Ghi kết quả
            self._write_result(result, is_proved, output_path)

            # Kết thúc tính thời gian
            end_time = time.time()
            
            # Tính toán thời gian chạy
            elapsed_time = end_time - start_time
            print(f"Đã xử lý thành công file {input_filename} trong {elapsed_time:.7f} giây")
            
        except Exception as e:
            print(f"Lỗi khi xử lý file {input_filename}: {str(e)}")

    def process_all_files(self) -> None:
        """
        Xử lý tất cả các file trong thư mục input
        """
        input_files = self._get_sorted_input_files()
        
        if not input_files:
            print("Không tìm thấy file input nào!")
            return

        for filename in input_files:
            self.process_single_file(filename)


def main():
    """
    Hàm main điều khiển luồng chính của chương trình
    """
    try:
        # Khởi tạo resolver
        resolver = LogicResolver()
        
        # Xử lý tất cả các file
        resolver.process_all_files()
        
        print("Hoàn thành xử lý tất cả các file!")
        
    except Exception as e:
        print(f"Lỗi trong quá trình thực thi: {str(e)}")


if __name__ == "__main__":
    main()