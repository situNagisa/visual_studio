import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

class MSBuildProject:
    def __init__(
            self
            , user_include_directories: list[str] = None
            , system_include_directories: list[str] = None
            , macros: dict[str, str] = None
    ):
        self.macros: dict[str, str] = macros or {}
        self.user_include_directories: list[str] = user_include_directories or []
        self.system_include_directories: list[str] = system_include_directories or []
    
    def add_macro(self, macro_name: str, macro_path: str):
        self.macros[macro_name] = macro_path
    
    def generate_xml(self) -> ET.Element:
        project = ET.Element("Project", {
            "ToolsVersion": "4.0",
            "xmlns": "http://schemas.microsoft.com/developer/msbuild/2003"
        })
        import_group = ET.SubElement(project, "ImportGroup", {"Label": "PropertySheets"})
        use_macros_property_group = ET.SubElement(project, "PropertyGroup", {"Label": "UserMacros"})
        # 添加现有的宏
        for macro, value in self.macros.items():
            macro_elem = ET.SubElement(use_macros_property_group, macro)
            macro_elem.text = value
        
        property_group = ET.SubElement(project, "PropertyGroup")
        if len(self.system_include_directories):
            include_directories = ET.SubElement(property_group, "IncludePath")
            include_directories.text = ''.join([f"{dir};" for dir in self.system_include_directories])
        
        item_def_group = ET.SubElement(project, "ItemDefinitionGroup")
        if len(self.user_include_directories):
            cl_compile = ET.SubElement(item_def_group, "ClCompile")
            additional_include_directories = ET.SubElement(cl_compile, "AdditionalIncludeDirectories")
            additional_include_directories.text = ''.join([f"{dir};" for dir in self.user_include_directories])
        
        build_macros = ET.SubElement(project, "ItemGroup")
        for macro, value in self.macros.items():
            macro_elem = ET.SubElement(build_macros, "BuildMacro", {"Include": macro})
            value_elem = ET.SubElement(macro_elem, "Value")
            value_elem.text = value
            env_variable = ET.SubElement(macro_elem, "EnvironmentVariable")
            env_variable.text = 'true'
        
        return project


def output_xml(project: ET.Element, output_file: os.path):
    # 将XML树写入文件
    tree = ET.ElementTree(project)
    raw_str = ET.tostring(project, 'utf-8')
    
    # 使用minidom进行美化
    dom = xml.dom.minidom.parseString(raw_str)
    pretty_xml_as_string = dom.toprettyxml(indent="  ")
    
    # tree.write('property_sheet.xml', encoding='utf-8', xml_declaration=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_as_string)

import pathlib


def is_library(dir: pathlib.Path) -> bool:
    include = dir / "include"
    return include.exists() and include.is_dir()

def get_library_path(cur: pathlib.Path, lib: pathlib.Path, relative=True) -> str:
    if relative:
        return str(lib.relative_to(cur))
    return str(lib.resolve())

def _search_library(root: pathlib.Path, cur: pathlib.Path, recurse=False, relative=True) -> list[str]:
    result: list[str] = []
    for entry in cur.iterdir():
        assert isinstance(entry, pathlib.Path)
        if not is_library(entry):
            if entry.is_dir() and recurse:
                result += _search_library(root, entry, recurse, relative)
            continue
        result.append(get_library_path(root, entry / "include", relative))
    return result
        
def search_library(path: pathlib.Path, recurse=False, relative=True) -> list[str]:
    return _search_library(path, path, recurse, relative)