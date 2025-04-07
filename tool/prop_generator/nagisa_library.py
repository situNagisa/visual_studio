import os
import argparse
import pathlib
import msbuild
from msbuild import MSBuildProject, output_xml, search_library
import json

def create() -> MSBuildProject:
    result = MSBuildProject()
    nagisa_library_root: str = os.environ.get("NAGISA_LIBRARY_ROOT")
    with open(os.path.join(nagisa_library_root, "nagisa_library.json"), "r", encoding="utf-8") as file:
        data = json.load(file)
    for lib_name, lib in data['installed'].items():
        if not msbuild.is_library(pathlib.Path(nagisa_library_root) / lib_name):
            raise RuntimeError(f"{lib_name} is not library")
        result.system_include_directories.append(f"$(NAGISA_LIBRARY_ROOT)/{lib_name}/include")
    result.system_include_directories.append('$(IncludePath)')
    return result


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='Generate and format MSBUILD property sheet.')
    parser.add_argument('--output', default="nagisa_library.props", help='output file name.')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    project = create()
    
    output_xml(project.generate_xml(), args.output)
    
    print("属性表已生成。")


if __name__ == "__main__":
    main()
