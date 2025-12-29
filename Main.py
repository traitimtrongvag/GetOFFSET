import re
from pathlib import Path
from rich.progress import Progress

INPUT_DIR = Path("INPUT")
OUTPUT_DIR = Path("OUTPUT")
INPUT_FILE = INPUT_DIR / "INPUT.txt"
OUTPUT_FILE = OUTPUT_DIR / "OUTPUT.txt"
ERROR_FILE = OUTPUT_DIR / "ERROR.txt"
DEFAULT_OLD_DUMP = "Dump_old.cs"
DEFAULT_NEW_DUMP = "Dump.cs"

CLASS_PATTERN = re.compile(
    r"^\s*(?:public|private|internal|protected)?\s*"
    r"(?:sealed\s+|static\s+|abstract\s+)?class\s+([\w\.<>\+]+)"
)
METHOD_PATTERN = re.compile(
    r"^\s*(?:public|private|protected|internal).*?\)\s*;\s*//\s*(0x[0-9a-fA-F]+)"
)
OFFSET_PATTERN = re.compile(r"0x[0-9a-fA-F]+")

def clean_signature(signature: str) -> str:
    signature = re.sub(
        r"^(?:public|private|protected|internal|static|virtual|sealed|extern|override|\s)+",
        "",
        signature
    )
    signature = re.sub(r"^(?:System\.)?\w+\s+", "", signature, count=1)
    signature = re.sub(r"<[^>]*>", "<>", signature)
    signature = signature.strip().rstrip(";")
    if not signature.endswith(")"):
        signature += "()"
    return signature.strip()

def parse_dump(dump_path: Path):
    offset_to_info = {}
    info_to_offset = {}
    class_stack = []
    
    with open(dump_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    brace_depth = 0
    
    with Progress() as progress:
        task = progress.add_task(f"[cyan]Parsing {dump_path.name}...", total=len(lines))
        for line in lines:
            class_match = CLASS_PATTERN.search(line)
            if class_match:
                class_name = class_match.group(1)
                full_class = f"{class_stack[-1]}+{class_name}" if class_stack else class_name
                class_stack.append(full_class)
            
            brace_depth += line.count("{") - line.count("}")
            for _ in range(line.count("}")):
                if class_stack and brace_depth < len(class_stack):
                    class_stack.pop()
            
            if class_stack:
                method_match = METHOD_PATTERN.search(line)
                if method_match:
                    current_class = class_stack[-1]
                    signature = clean_signature(line.split("//")[0].strip())
                    offset = method_match.group(1)
                    offset_to_info[offset] = (current_class, signature)
                    info_to_offset[(current_class, signature)] = offset
            
            progress.advance(task)
    
    return offset_to_info, info_to_offset

def map_offsets(old_dump_path: Path, new_dump_path: Path, offsets: list):
    old_map, _ = parse_dump(old_dump_path)
    _, new_map = parse_dump(new_dump_path)
    results = {}
    
    for offset in offsets:
        if offset not in old_map:
            results[offset] = (None, None, None)
            continue
        
        class_name, signature = old_map[offset]
        new_offset = new_map.get((class_name, signature))
        
        if not new_offset:
            fallback_signature = re.sub(r"b__\d+_\d+", "b", signature)
            new_offset = new_map.get((class_name, fallback_signature))
        
        results[offset] = (new_offset, class_name, signature)
    
    return results

def process_input(old_dump_path: Path, new_dump_path: Path):
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        input_lines = f.readlines()
    
    all_offsets = list(dict.fromkeys(OFFSET_PATTERN.findall("".join(input_lines))))
    mapped_offsets = map_offsets(old_dump_path, new_dump_path, all_offsets)
    
    error_offsets = []
    success_count = 0
    
    with Progress() as progress, open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        task = progress.add_task("[green]Processing input file...", total=len(input_lines))
        for line in input_lines:
            def replace_offset(match):
                offset = match.group(0)
                new_offset, _, _ = mapped_offsets.get(offset, (None, None, None))
                return new_offset if new_offset else offset
            f_out.write(OFFSET_PATTERN.sub(replace_offset, line))
            progress.advance(task)
    
    for old_offset, (new_offset, class_name, signature) in mapped_offsets.items():
        status = new_offset if new_offset else "NOT FOUND"
        print(f"{old_offset} -> {status}   [{class_name}] {signature}")
        
        if not new_offset:
            error_offsets.append((old_offset, class_name, signature))
        else:
            success_count += 1
    
    if error_offsets:
        with open(ERROR_FILE, "w", encoding="utf-8") as f_error:
            f_error.write("ERROR OFFSETS - NOT FOUND\n")
            f_error.write("=" * 80 + "\n\n")
            for old_offset, class_name, signature in error_offsets:
                f_error.write(f"{old_offset} -> NOT FOUND\n")
                f_error.write(f"  Class: {class_name}\n")
                f_error.write(f"  Signature: {signature}\n\n")
        
        print(f"\n[ERROR] {len(error_offsets)} offset(s) not found!")
        print(f"[SUCCESS] {success_count} offset(s) mapped successfully!")
        print(f"Error details saved to {ERROR_FILE}")
    else:
        print(f"\n[SUCCESS] {success_count} offset(s) mapped successfully!")
        print("Congratulations! No errors found!")
    
    print(f"\nDone! Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    old_dump_input = input(f"Enter old dump file (default {DEFAULT_OLD_DUMP}): ").strip()
    new_dump_input = input(f"Enter new dump file (default {DEFAULT_NEW_DUMP}): ").strip()
    
    old_dump_path = Path(old_dump_input) if old_dump_input else Path(DEFAULT_OLD_DUMP)
    new_dump_path = Path(new_dump_input) if new_dump_input else Path(DEFAULT_NEW_DUMP)
    
    process_input(old_dump_path, new_dump_path)