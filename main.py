import os

folder_path = "C:/Users/agiview/Desktop/日志/middleware"
search_string = ["EXCEPTION", "exception", "Exception"]
filter_string = []


def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if any(substring in line for substring in search_string) and not any(substring in line for substring in filter_string):
                    print(line.strip())
    except Exception as e:
        print(f"处理文件时出错: {file_path}\n{str(e)}")


def traverse_directory(folder_path):
    try:
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                process_file(file_path)
    except Exception as e:
        print(f"遍历文件夹时出错: {folder_path}\n{str(e)}")


if __name__ == "__main__":
    traverse_directory(folder_path)
