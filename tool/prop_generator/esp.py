import os
import argparse
import json
from msbuild import MSBuildProject, output_xml

env_idf_tools_path = os.environ.get("IDF_TOOLS_PATH")

def create_esp_project(
		idf_path: os.path
		, chip: str
) -> MSBuildProject:
	support_chips: list[str] = [
		'linux',
		'esp32',
		'esp32c2', 'esp32c3', 'esp32c5', 'esp32c6', 'esp32c61',
		'esp32s2', 'esp32s3',
		'esp32h2', 'esp32h4',
		'esp32p4',
	]
	if chip not in support_chips:
		raise ValueError(f"Unknown chip: {chip}")
	
	result = MSBuildProject(
		user_include_directories=[
			'%(AdditionalIncludeDirectories)',
			"$(ProjectDir)/build/config"
		],
		macros={"IDF_PATH": idf_path}
	)
	def search_directory(searched_directory: os.path):
		for root, dirs, files in os.walk(searched_directory):
			if chip in dirs:
				for c in support_chips:
					if c not in dirs:
						continue
					dirs.remove(c)
				dirs.append(chip)

			for dir in dirs:
				if dir.startswith("test"):
					dirs.remove(dir)

			if 'include' in dirs:
				dirs.remove('include')
				relative_path = os.path.relpath(os.path.join(root, 'include'), idf_path)
				result.system_include_directories.append(f"$(IDF_PATH)/{relative_path}")
	
	search_directory(os.path.join(idf_path, "components"))
	# search_directory(os.path.join(idf_path, "examples"))
	
	return result

def main():
	# 创建命令行参数解析器
	parser = argparse.ArgumentParser(description='Generate and format MSBUILD property sheet.')
	parser.add_argument('--output_dir', default='esp_idf', help='output path.')
	parser.add_argument('--idf_tools_path', default=f"{env_idf_tools_path}", help='Path to ESP-IDF tool root.')
	
	# 解析命令行参数
	args = parser.parse_args()
	with open(os.path.join(args.idf_tools_path, "idf-env.json"), "r", encoding="utf-8") as file:
		data = json.load(file)
	os.makedirs(args.output_dir, exist_ok=True)
	for release in data["idfInstalled"].values():
		for chip in release["targets"]:
			project = create_esp_project(release["path"], chip)
			
			output_xml(project.generate_xml(), os.path.join(args.output_dir, f"{chip}-{release['version']}.props"))

	print("属性表已生成。")


if __name__ == "__main__":
	main()
