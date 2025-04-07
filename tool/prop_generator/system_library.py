import os
import argparse
import pathlib
from msbuild import MSBuildProject, output_xml, search_library

def create_system_library_project(
        env: str
        , input_dir: pathlib.Path
) -> MSBuildProject:
    result = MSBuildProject(
        system_include_directories=['$(IncludePath)']
    )
    
    include_dirs = search_library(input_dir, recurse=False, relative=True)
    for d in include_dirs:
        result.system_include_directories.append(f"$({env})/{d}")
    
    return result

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='Generate and format MSBUILD property sheet.')
    parser.add_argument('--env-name', help='the environment variable name that include libraries')
    parser.add_argument('--output', help='output file name.')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    env: str = args.env_name
    input_dir: str = os.environ.get(env)
    
    project = create_system_library_project(env, pathlib.Path(input_dir))
            
    output_xml(project.generate_xml(), args.output)
    
    print("属性表已生成。")


if __name__ == "__main__":
    main()
