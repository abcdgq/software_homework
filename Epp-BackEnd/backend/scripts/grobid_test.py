import os
import requests

import xml.etree.ElementTree as ET
from pathlib import Path
import json

server_ip = '115.190.109.233'

def getXml(input_file_path, output_dir, i):
    url = f"http://{server_ip}:8070/api/processFulltextDocument"
    # filename = "outputf"
    params = dict(input = open(str(input_file_path), 'rb'))
    response = requests.post(url, files=params, timeout=3000000)
    # print(response.text)
    # output_path = os.path.join(output_dir, filename + str(i+1) + ".xml")
    # print("output: ", output_path)
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)
    # fh = open(output_path, "w", encoding="utf-8")
    # fh.write(response.text)
    # fh.close()
    return response.text

def parse_grobid_xml(xml_content):
    """解析GROBID XML并提取结构化内容"""
    # 注册命名空间
    ns = {
        'tei': 'http://www.tei-c.org/ns/1.0',
        'xml': 'http://www.w3.org/XML/1998/namespace'
    }

    root = ET.fromstring(xml_content)
    result = {
        "metadata": {},
        "sections": [],
        "references": []
    }

    # ========== 提取元数据 ==========
    # 标题
    title_elem = root.find('.//tei:titleStmt/tei:title', ns)
    result["metadata"]["title"] = title_elem.text.strip() if title_elem is not None else ""

    # 作者信息
    authors = []
    for author_elem in root.findall('.//tei:sourceDesc//tei:author', ns):
        author = {}
        if (persName := author_elem.find('tei:persName', ns)) is not None:
            author["name"] = " ".join([
                persName.findtext('tei:forename', '', ns).strip(),
                persName.findtext('tei:surname', '', ns).strip()
            ]).strip()
        
        # 提取作者机构
        if (affiliation := author_elem.find('tei:affiliation', ns)) is not None:
            orgs = []
            for org in affiliation.findall('tei:orgName', ns):
                orgs.append({
                    "name": org.text.strip(),
                    "type": org.get("type", "")
                })
            author["affiliations"] = orgs
        
        authors.append(author)
    result["metadata"]["authors"] = authors

    # ========== 提取摘要 ==========
    abstract_elem = root.find('.//tei:profileDesc/tei:abstract/tei:div/tei:p', ns)
    result["metadata"]["abstract"] = abstract_elem.text.strip() if abstract_elem is not None else ""

    # ========== 提取正文章节 ==========
    section_keywords = {
        "RelatedWork":  ["related work", "literature review", "研究现状", "相关工作", "背景"],
        "Methodology":  ["methodology", "proposed method", "方法", "模型设计", "算法"],
        "Experiments":  ["experiments", "evaluation", "实验", "结果分析", "数据集"],
        "Conclusion":   ["conclusion", "总结", "未来工作", "concluding remarks"]
    }
    
    for div in root.findall('.//tei:body/tei:div', ns):
        section = {
            "n": "",
            "title": div.findtext('tei:head', '', ns).strip(),
            "content": [],
            "paragraphs": []
        }

        if (n_attr := div.find('tei:head', ns).get("n")) is not None:
            section["n"] = n_attr.strip()

        # TODO 分块逻辑
        # Introduction , Related work, Experiments, Conclusion（可能包含Future Work）的章标题较为固定，其中Experiments可能有多章，
        # 可以将Related work后到Experiments之间视为解决方法部分，Experiments第一次出现的地方到Conclusion前视为实验部分
        # 部分文章Related work/Introduction（若无Related work）与Conclusion之间仅有一章，同时视为Experiments与解决方法？（）
        # 部分文章没有Related work，将Introduction视为研究现状？
        # 部分文章没有实验部分，将实验与解决方法合并？
        # 部分文章没有结论部分，只有Discussion

        # 分块顺序：先找Introduction和Conclusion，再找有没有Related work，再找Experiments，
        # 如果之间有，则将那部分视为解决方法，如果没有，将实验与解决方法合并

        # 提取段落
        for p in div.findall('tei:p', ns):
            paragraph = {
                "text": "".join(p.itertext()).strip(),
                "citations": []
            }

            # 提取段落内引用
            for ref in p.findall('tei:ref', ns):
                if ref.get("type") == "bibr":
                    paragraph["citations"].append({
                        "target": ref.get("target", "").replace("#", ""),
                        "text": "".join(ref.itertext()).strip()
                    })
            
            section["paragraphs"].append(paragraph)
            section["content"].append(paragraph["text"])  # 兼容旧字段
        
        result["sections"].append(section)

    # ========== 提取参考文献 ==========
    for bibl in root.findall('.//tei:listBibl/tei:biblStruct', ns):
        ref = {
            "id": bibl.get("{http://www.w3.org/XML/1998/namespace}id", ""),
            "title": "",
            "authors": [],
            "date": "",
            "journal": ""
        }

        # 提取标题
        if (title := bibl.find('tei:analytic/tei:title', ns)) is not None:
            ref["title"] = title.text.strip()

        # 提取作者
        ref_authors = []
        for author in bibl.findall('tei:analytic/tei:author', ns):
            ref_authors.append(" ".join([
                author.findtext('tei:persName/tei:forename', '', ns).strip(),
                author.findtext('tei:persName/tei:surname', '', ns).strip()
            ]))
        ref["authors"] = ref_authors

        # 提取期刊信息
        if (monogr := bibl.find('tei:monogr', ns)) is not None:
            ref["journal"] = monogr.findtext('tei:title', '', ns).strip()
            ref["date"] = monogr.findtext('tei:imprint/tei:date', '', ns).strip()

        result["references"].append(ref)

    return result

import json
from typing import List, Dict

def reorganize_sections(original_data: Dict) -> Dict:
    """
    重组章节结构为五部分标准格式
    返回数据结构示例：
    {
        "metadata": {...},
        "sections": {
            "Introduction": [...],
            "RelatedWork": [...],
            "Methodology": [...],
            "Experiments": [...],
            "Conclusion": [...]
        }
    }
    """
    # 定义关键词映射表(可根据需要扩展)
    KEYWORD_MAP = {
        "Introduction": ["introduction", "literature review", "引言", "背景", "研究现状", "背景"],
        "RelatedWork": ["related work", "相关工作", "文献综述"],
        "Experiments": ["experiment", "evaluation", "实验", "结果分析", "评估"],
        "Conclusion": ["conclusion", "concluding remarks", "总结", "结论", "展望", "未来工作"]
    }

    # 初始化索引标记
    section_index = {
        "Introduction": {"start": None, "end": None},
        "RelatedWork": {"start": None, "end": None},
        "Experiments": {"start": None, "end": None},
        "Conclusion": {"start": None, "end": None}
    }

    # 获取原始章节列表
    raw_sections = original_data.get("sections", [])
    total_sections = len(raw_sections)

    # === 步骤1：定位关键章节 ===
    # 记录所有章节的匹配情况
    matches = {k: [] for k in KEYWORD_MAP}
    for idx, simplified_sec in enumerate(raw_sections):
        title = simplified_sec["title"].lower()
        for part, keywords in KEYWORD_MAP.items():
            if any(kw in title for kw in keywords):
                matches[part].append(idx)

    # === 步骤2：确定各部分边界 ===
    # 1. Introduction逻辑
    if matches["Introduction"]:
        section_index["Introduction"]["start"] = matches["Introduction"][0]
        section_index["Introduction"]["end"] = matches["Introduction"][0]
    else:
        section_index["Introduction"]["start"] = 0  # 默认第一章
        section_index["Introduction"]["end"] = 0

    # 2. Conclusion逻辑
    if matches["Conclusion"]:
        section_index["Conclusion"]["start"] = matches["Conclusion"][-1]  # 取最后一个匹配项
        section_index["Conclusion"]["end"] = matches["Conclusion"][-1]
    else:
        section_index["Conclusion"]["start"] = total_sections - 1  # 默认最后一章
        section_index["Conclusion"]["end"] = total_sections - 1

    # 3. RelatedWork逻辑
    if matches["RelatedWork"]:
        rel_match = matches["RelatedWork"][0]
        start, end = get_subsection_range(raw_sections, rel_match)
        section_index["RelatedWork"]["start"] = start
        section_index["RelatedWork"]["end"] = end
    else:
        # 使用Introduction章节作为RelatedWork
        section_index["RelatedWork"]["start"] = section_index["Introduction"]["start"]
        section_index["RelatedWork"]["end"] = section_index["Introduction"]["end"]

    # 4. Experiments逻辑
    if matches["Experiments"]:
        exp_match = matches["Experiments"][0]
        exp_start, exp_end =  get_subsection_range(raw_sections, exp_match)
        section_index["Experiments"]["start"] = exp_start
        section_index["Experiments"]["end"] = section_index["Conclusion"]["start"] - 1
    else:
        # RelatedWork到Conclusion之间的内容
        section_index["Experiments"]["start"] = section_index["RelatedWork"]["end"] + 1
        section_index["Experiments"]["end"] = section_index["Conclusion"]["start"] - 1

    # 5. Methodology逻辑
    methodology_start = section_index["RelatedWork"]["end"] + 1
    methodology_end = section_index["Experiments"]["start"] - 1
    if methodology_start > methodology_end:
        # 没有独立章节时使用Experiments内容
        methodology_start = section_index["Experiments"]["start"]
        methodology_end = section_index["Experiments"]["end"]

    # === 步骤3：构建新结构 ===
    new_structure = {
        "metadata": original_data["metadata"],
        "sections": {
            "Introduction": [],
            "RelatedWork": [],
            "Methodology": [],
            "Experiments": [],
            "Conclusion": []
        }
    }

    # 填充各分区内容
    for idx, sec in enumerate(raw_sections):
        simplified_sec = {
            "title": sec["title"],
            "content": sec["content"]  # 直接使用content数组
        }

        # Introduction
        if section_index["Introduction"]["start"] <= idx <= section_index["Introduction"]["end"]:
            new_structure["sections"]["Introduction"].append(simplified_sec)
        
        # RelatedWork
        if section_index["RelatedWork"]["start"] <= idx <= section_index["RelatedWork"]["end"]:
            new_structure["sections"]["RelatedWork"].append(simplified_sec)
        
        # Methodology
        if methodology_start <= idx <= methodology_end:
            new_structure["sections"]["Methodology"].append(simplified_sec)
        
        # Experiments
        if section_index["Experiments"]["start"] <= idx <= section_index["Experiments"]["end"]:
            new_structure["sections"]["Experiments"].append(simplified_sec)
        
        # Conclusion
        if idx == section_index["Conclusion"]["start"]:
            new_structure["sections"]["Conclusion"].append(simplified_sec)

    return new_structure

def get_parent_section_num(section_number: str) -> str:
    """
    根据章节号获取顶层章节号
    """
    # 去除末尾可能存在的点（如 "2." -> "2"）
    cleaned = section_number.rstrip('.')
    # 找到第一个分隔符的位置
    dot_pos = cleaned.find('.')
    return cleaned[:dot_pos] if dot_pos != -1 else cleaned

def get_subsection_range(sections, index):
    """
    获取指定索引的所有子章节范围（起止索引）
    """

    n = sections[index]["n"]
    if n == "":
        return index, index
    
    start_idx = -1
    end_idx = -1
    parent_section_num = get_parent_section_num(n)
    
    # 遍历查找所有匹配章节
    for idx, sec in enumerate(sections):
        cur_n = sec["n"]
        if cur_n != "" and parent_section_num == get_parent_section_num(cur_n):
            if start_idx == -1:
                start_idx = idx
            end_idx = idx
    
    # 处理未找到的情况
    if start_idx == -1:
        return index, index
    
    return start_idx, end_idx

def run(files_paths, output_file_path):
    for i, file_path in enumerate(files_paths) :
        print("i file_path:", file_path)
        getXml(file_path, output_file_path, i)

if __name__ ==  "__main__":
    # output_dir = "grobid_output"
    # # input_path = [os.path.join("sam.pdf")]
    # input_file_path = "./Epp-BackEnd/backend/resource/uploads/users/documents/2017-NeurIPS-Neural Discrete Representation Learning20250504184945_69.pdf"
    # print("path: ", input_file_path)
    # # run(input_path, output_path)
    # xml = getXml(input_file_path, output_dir, 0)

    # parsed_data = parse_grobid_xml(xml)
    # print(parsed_data)
    # output_file = os.path.join(output_dir, "output1.json")
    # with open(output_file, "w", encoding="utf-8") as f:
    #     json.dump(parsed_data, f, ensure_ascii=False, indent=4)
    
    # sections = reorganize_sections(parsed_data)
    # output_file = os.path.join(output_dir, "output2.json")
    # with open(output_file, "w", encoding="utf-8") as f:
    #     json.dump(sections, f, ensure_ascii=False, indent=4)

    print(get_parent_section_num(str(3.2)))

