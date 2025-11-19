import re
from rich.progress import Progress

def clean_signature(str_sig: str) -> str:
    str_sig = re.sub(r"^(?:public|private|protected|internal|static|virtual|sealed|extern|override|\s)+", "", str_sig)
    str_sig = re.sub(r"^(?:System\.)?\w+\s+", "", str_sig, count=1)
    str_sig = re.sub(r"<[^>]*>", "<>", str_sig)
    str_sig = str_sig.strip().rstrip(";")
    if not str_sig.endswith(")"):
        str_sig += "()"
    return str_sig.strip()

def parse_dump(str_path: str):
    g_offset_to_info = {}
    g_info_to_offset = {}
    g_class_stack = []

    m_class_pattern = re.compile(r"^\s*(?:public|private|internal|protected)?\s*(?:sealed\s+|static\s+|abstract\s+)?class\s+([\w\.<>\+]+)")
    m_method_pattern = re.compile(r"^\s*(?:public|private|protected|internal).*?\)\s*;\s*//\s*(0x[0-9a-fA-F]+)")

    with open(str_path, "r", encoding="utf-8", errors="ignore") as f:
        g_lines = f.readlines()

    brace_depth = 0

    with Progress() as g_progress:
        task = g_progress.add_task(f"[cyan]Parsing {str_path}...", total=len(g_lines))
        for str_line in g_lines:
            m_cls = m_class_pattern.search(str_line)
            if m_cls:
                cls_name = m_cls.group(1)
                full_cls = f"{g_class_stack[-1]}+{cls_name}" if g_class_stack else cls_name
                g_class_stack.append(full_cls)

            brace_depth += str_line.count("{") - str_line.count("}")
            for _ in range(str_line.count("}")):
                if g_class_stack and brace_depth < len(g_class_stack):
                    g_class_stack.pop()

            if g_class_stack:
                m_method = m_method_pattern.search(str_line)
                if m_method:
                    g_current_class = g_class_stack[-1]
                    str_sig = clean_signature(str_line.split("//")[0].strip())
                    g_offset = m_method.group(1)
                    g_offset_to_info[g_offset] = (g_current_class, str_sig)
                    g_info_to_offset[(g_current_class, str_sig)] = g_offset

            g_progress.advance(task)

    return g_offset_to_info, g_info_to_offset

def map_offsets(str_old_dump: str, str_new_dump: str, g_offsets: list):
    g_old_map, _ = parse_dump(str_old_dump)
    _, g_new_map = parse_dump(str_new_dump)
    g_results = {}

    for g_off in g_offsets:
        if g_off not in g_old_map:
            g_results[g_off] = (None, None, None)
            continue
        g_cls, str_sig = g_old_map[g_off]
        g_new_off = g_new_map.get((g_cls, str_sig))
        if not g_new_off:
            fallback_sig = re.sub(r"b__\d+_\d+", "b", str_sig)
            g_new_off = g_new_map.get((g_cls, fallback_sig))
        g_results[g_off] = (g_new_off, g_cls, str_sig)

    return g_results

def process_input(str_input_file="INPUT.txt", str_output_file="OUTPUT.txt",
                  str_old_dump="dump_old.cs", str_new_dump="dump.cs"):
    with open(str_input_file, "r", encoding="utf-8", errors="ignore") as f:
        g_input_lines = f.readlines()

    g_all_offsets = list(dict.fromkeys(re.findall(r"0x[0-9a-fA-F]+", "".join(g_input_lines))))
    g_mapped_offsets = map_offsets(str_old_dump, str_new_dump, g_all_offsets)

    with Progress() as g_progress, open(str_output_file, "w", encoding="utf-8") as f_out:
        task = g_progress.add_task("[green]Processing input file...", total=len(g_input_lines))
        for str_line in g_input_lines:
            def replace_offset(m):
                g_off = m.group(0)
                g_new_off, _, _ = g_mapped_offsets.get(g_off, (None, None, None))
                return g_new_off if g_new_off else g_off
            f_out.write(re.sub(r"0x[0-9a-fA-F]+", replace_offset, str_line))
            g_progress.advance(task)

    for g_old, (g_new, g_cls, str_sig) in g_mapped_offsets.items():
        print(f"{g_old} -> {g_new if g_new else 'NOT FOUND'}   [{g_cls}] {str_sig}")

    print(f"\nDone! Output saved to {str_output_file}")

if __name__ == "__main__":
    str_old_dump = input("Enter old dump file (default dump_old.cs): ").strip() or "dump_old.cs"
    str_new_dump = input("Enter new dump file (default dump.cs): ").strip() or "dump.cs"
    process_input("INPUT.txt", "OUTPUT.txt", str_old_dump, str_new_dump)
