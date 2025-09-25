import re
from rich.progress import Progress

# ------------------------------
# Helper functions
# ------------------------------

def clean_signature(str_sig: str) -> str:
    """
    Remove compiler-generated patterns like b__xxx_y in a method signature.
    We keep the original class/generic info intact.
    """
    str_sig = re.sub(r"(<[^>]+>)b__\d+_\d+", r"\1", str_sig)
    if not str_sig.endswith(")"):
        str_sig = str_sig.rstrip(";") + "()"
    return str_sig.strip()


def parse_dump(str_path: str):
    """
    Parse a dump.cs file:
      - g_offset_to_info: dict mapping offset -> (full_class, signature)
      - g_info_to_offset: dict mapping (full_class, signature) -> offset
    """
    g_offset_to_info = {}
    g_info_to_offset = {}

    g_current_class = None

    # Match full class name like A.B.C
    m_class_pattern = re.compile(r"^\s*(?:public|private|internal)\s+class\s+([\w\.]+)")
    m_method_pattern = re.compile(
        r"^\s*(public|private|protected|internal).*?\)\s*;\s*//\s*(0x[0-9a-fA-F]+)"
    )

    with open(str_path, "r", encoding="utf-8", errors="ignore") as f:
        g_lines = f.readlines()

    # Show progress bar for user feedback
    with Progress() as g_progress:
        task = g_progress.add_task(f"[cyan]Parsing {str_path}...", total=len(g_lines))

        for str_line in g_lines:
            m_cls = m_class_pattern.search(str_line)
            if m_cls:
                g_current_class = m_cls.group(1)
            else:
                m_method = m_method_pattern.search(str_line)
                if m_method and g_current_class:
                    str_sig = str_line.split("//")[0].strip()
                    str_sig = clean_signature(str_sig)
                    g_offset = m_method.group(2)
                    g_offset_to_info[g_offset] = (g_current_class, str_sig)
                    g_info_to_offset[(g_current_class, str_sig)] = g_offset

            g_progress.advance(task)

    return g_offset_to_info, g_info_to_offset


# ------------------------------
# Mapping old offsets to new
# ------------------------------

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
        g_results[g_off] = (g_new_off, g_cls, str_sig)

    return g_results


# ------------------------------
# Main processing
# ------------------------------

def process_input(str_input_file="INPUT.txt", str_output_file="OUTPUT.txt",
                  str_old_dump="dump_old.cs", str_new_dump="dump.cs"):

    # Read all offsets from input
    with open(str_input_file, "r", encoding="utf-8", errors="ignore") as f:
        g_input_lines = f.readlines()

    g_all_offsets = re.findall(r"0x[0-9a-fA-F]+", "".join(g_input_lines))
    g_all_offsets = list(dict.fromkeys(g_all_offsets))  # remove duplicates, keep order

    # Map old offsets to new offsets
    g_mapped_offsets = map_offsets(str_old_dump, str_new_dump, g_all_offsets)

    # Replace offsets in each line with progress
    with Progress() as g_progress, open(str_output_file, "w", encoding="utf-8") as f_out:
        task = g_progress.add_task("[green]Processing input file...", total=len(g_input_lines))

        for str_line in g_input_lines:

            def replace_offset(m):
                g_off = m.group(0)
                g_new_off, _, _ = g_mapped_offsets.get(g_off, (None, None, None))
                # if not found, keep original offset
                return g_new_off if g_new_off else g_off

            str_new_line = re.sub(r"0x[0-9a-fA-F]+", replace_offset, str_line)
            f_out.write(str_new_line)
            g_progress.advance(task)

    # Show mapping result for user clarity
    print("=== Offset Mapping Result ===")
    for g_old, (g_new, g_cls, str_sig) in g_mapped_offsets.items():
        if g_new:
            print(f"{g_old} -> {g_new}   [{g_cls}] {str_sig}")
        else:
            print(f"{g_old} -> NOT FOUND in new dump")

    print(f"\nDone! Output saved to {str_output_file}")


# ------------------------------
# Entry point
# ------------------------------

if __name__ == "__main__":
    str_old_dump = input("Enter old dump file (default dump_old.cs): ").strip() or "dump_old.cs"
    str_new_dump = input("Enter new dump file (default dump.cs): ").strip() or "dump.cs"

    process_input("INPUT.txt", "OUTPUT.txt", str_old_dump, str_new_dump)
