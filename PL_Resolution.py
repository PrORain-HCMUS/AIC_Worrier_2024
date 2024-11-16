import os
import kb
import re

INPUT_DIR = './input/'
OUTPUT_DIR = './output/'


def readKB(filename):
    content = []
    with open(filename, 'r', encoding='utf-8-sig') as f:
        content = f.read().splitlines()

    # Loại bỏ các dòng trống
    content = [line.strip() for line in content if line.strip()]
    
    # Dòng 1 chứa query letter (B)
    query_letter = content[0]
    
    # Dòng 2 chứa số lượng mệnh đề trong KB (2)
    kb_size = int(content[1])
    
    # Các dòng còn lại là các mệnh đề
    kb_string = content[2:]
    
    # Tạo query dựa trên query letter
    query = [[query_letter]]
    
    # Tạo Knowledge Base
    KB = kb.KnowledgeBase()
    for cnf in kb_string:
        clause = cnf.split()
        clause = list(filter(lambda x: x != 'OR', clause))
        KB.addClause(clause)

    return KB, query


def writeOutput(result, check, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for loop_res in result:
            f.write(str(len(loop_res)) + '\n')
            for clause in loop_res:
                string = ''
                for c in clause:
                    string += c
                    if c != clause[-1]:
                        string += ' OR '
                f.write(string + '\n')
        if check:
            f.write('YES')
        else:
            f.write('NO')


# Get list of input files and sort them numerically
inputs = [f for f in os.listdir(INPUT_DIR) if f.startswith('input_') and f.endswith('.txt')]
inputs.sort(key=lambda x: int(re.search(r'input_(\d+)\.txt', x).group(1)))

# Thay đổi output_filename từ 'out-' + filename sang định dạng 'output_01.txt', 'output_02.txt', ...
for filename in inputs:
    try:
        KB, query = readKB(INPUT_DIR + filename)
        result, check = KB.PL_Resolution(query)

        # Lấy số từ tên file input để tạo tên file output
        match = re.search(r'input_(\d+)\.txt', filename)
        if match:
            file_number = match.group(1)
            output_filename = f'output_{file_number}.txt'
        
        writeOutput(result, check, OUTPUT_DIR + output_filename)
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")