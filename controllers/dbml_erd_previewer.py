# -*- coding: utf-8 -*-
"""
Convierte un archivo DBML o SQL a PlantUML y opcionalmente renderiza el ERD.

Uso:
    python controllers/dbml_erd_previewer.py archivo.dbml
    python controllers/dbml_erd_previewer.py archivo.dbml --render
"""

import argparse
import os
import re

from plantuml import PlantUML


def strip_comments(text: str) -> str:
    text = re.sub(r'(?m)--.*$', '', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    text = re.sub(r'//.*$', '', text, flags=re.M)
    return text


def is_dbml(text: str) -> bool:
    return bool(re.search(r'^[ \t]*(Table|Enum|Ref|Project|database)\b', text, re.I | re.M))


def parse_dbml_ref(op: str, left_table: str, left_col: str, right_table: str, right_col: str):
    if '<' in op:
        parent_table, parent_col = right_table, right_col
        child_table, child_col = left_table, left_col
    else:
        parent_table, parent_col = left_table, left_col
        child_table, child_col = right_table, right_col
    return parent_table, parent_col, child_table, child_col


def parse_dbml_ref_attr(attr_value: str, current_table: str, current_column: str):
    m = re.match(r'`?(\w+)`?\.(\w+)', attr_value)
    if not m:
        return None
    return m.group(1), m.group(2), current_table, current_column


def parse_dbml(text: str):
    text = strip_comments(text)
    tables = {}
    relationships = []

    table_re = re.compile(r'^[ \t]*Table\s+`?(\w+)`?\s*\{([^}]*)\}', re.I | re.M | re.S)
    for table_name, body in table_re.findall(text):
        columns = []
        for line in body.splitlines():
            line = line.strip()
            if not line or line.lower().startswith('indexes') or line.lower().startswith('note'):
                continue
            match = re.match(r'`?(\w+)`?\s+([^\[\n]+?)(?:\s*\[(.*?)\])?\s*$', line)
            if not match:
                continue
            col_name, col_type, attrs = match.groups()
            attrs_list = [a.strip().lower() for a in (attrs or '').split(',') if a.strip()]
            pk = any(attr in ('pk', 'primary key') for attr in attrs_list)
            columns.append({'name': col_name, 'type': col_type.strip(), 'pk': pk})
            for attr in attrs_list:
                if attr.startswith('ref:'):
                    parsed = parse_dbml_ref_attr(attr[len('ref:'):].strip(), table_name, col_name)
                    if parsed:
                        relationships.append(parsed)
        tables[table_name] = columns

    ref_line_re = re.compile(
        r'^[ \t]*Ref:\s*`?(\w+)`?\.(\w+)\s*([<>-]+)\s*`?(\w+)`?\.(\w+)',
        re.I | re.M,
    )
    for left_table, left_col, op, right_table, right_col in ref_line_re.findall(text):
        relationships.append(parse_dbml_ref(op, left_table, left_col, right_table, right_col))

    # Deduplicate relationships
    unique_relationships = []
    for rel in relationships:
        if rel not in unique_relationships:
            unique_relationships.append(rel)

    return tables, unique_relationships


def find_matching_paren(text: str, pos: int) -> int | None:
    depth = 0
    in_single = False
    in_double = False
    i = pos
    while i < len(text):
        c = text[i]
        if c == "'" and not in_double:
            in_single = not in_single
        elif c == '"' and not in_single:
            in_double = not in_double
        elif not in_single and not in_double:
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    return None


def split_sql_columns(body: str):
    fields = []
    current = ''
    depth = 0
    in_single = False
    in_double = False
    for ch in body:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double

        if not in_single and not in_double:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            if ch == ',' and depth == 0:
                if current.strip():
                    fields.append(current.strip())
                current = ''
                continue
        current += ch

    if current.strip():
        fields.append(current.strip())
    return fields


def parse_inline_fk(extras: str):
    match = re.search(r'REFERENCES\s+`?(\w+)`?\s*\(`?(\w+)`?\)', extras, re.I)
    if not match:
        return None
    return match.group(1), match.group(2)


def parse_sql(text: str):
    text = strip_comments(text)
    tables = {}
    relationships = []

    create_table_re = re.compile(
        r'CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?(`?\w+`?(?:\.\w+`?)?)\s*\(',
        re.I,
    )
    for match in create_table_re.finditer(text):
        header_start = match.start()
        body_start = match.end() - 1
        body_end = find_matching_paren(text, body_start)
        if body_end is None:
            continue

        header = text[header_start:match.end()]
        body = text[body_start + 1:body_end]
        table_name = match.group(2).strip('`')
        columns = []

        for item in split_sql_columns(body):
            line = item.strip()
            if not line or line.upper().startswith(('CONSTRAINT', 'PRIMARY KEY', 'UNIQUE', 'CHECK')):
                continue
            col_match = re.match(r'`?(\w+)`?\s+([^\s]+(?:\s*\([^)]*\))?)(.*)$', line, re.I)
            if col_match:
                col_name = col_match.group(1)
                col_type = col_match.group(2)
                extras = col_match.group(3)
                pk = bool(re.search(r'\bPRIMARY\s+KEY\b', extras, re.I))
                columns.append({'name': col_name, 'type': col_type, 'pk': pk})
                fk = parse_inline_fk(extras)
                if fk:
                    relationships.append((fk[0], fk[1], table_name, col_name))
                continue

            fk_match = re.search(
                r'FOREIGN\s+KEY\s*\(`?(\w+)`?\)\s*REFERENCES\s+`?(\w+)`?\s*\(`?(\w+)`?\)',
                line,
                re.I,
            )
            if fk_match:
                child_col, parent_table, parent_col = fk_match.groups()
                relationships.append((parent_table, parent_col, table_name, child_col))

        tables[table_name] = columns

        for constraint_match in re.finditer(
            r'CONSTRAINT\s+`?\w+`?\s+FOREIGN\s+KEY\s*\(`?(\w+)`?\)\s*REFERENCES\s+`?(\w+)`?\s*\(`?(\w+)`?\)',
            body,
            re.I,
        ):
            child_col, parent_table, parent_col = constraint_match.groups()
            relationships.append((parent_table, parent_col, table_name, child_col))

    return tables, relationships


def build_plantuml(tables, relationships):
    lines = [
        '@startuml',
        '!theme plain',
        'hide circle',
        'skinparam linetype ortho',
        '',
        "' Entity-Relationship diagram generated by dbml_erd_previewer",
        '',
    ]

    for table_name, columns in tables.items():
        lines.append(f'entity "{table_name}" as {table_name} {{')
        for col in columns:
            if col['pk']:
                lines.append(f'  * **{col["name"]}** : {col["type"]}')
            else:
                lines.append(f'  {col["name"]} : {col["type"]}')
        lines.append('}\n')

    for parent, parent_col, child, child_col in relationships:
        lines.append(f'{parent} ||--o{{ {child} : "{child_col} → {parent_col}"')

    lines.append('\n@enduml')
    return '\n'.join(lines)


def save_puml(path: str, content: str):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def render_puml(puml_path: str, output_dir: str) -> str:
    plantuml_server = PlantUML(url='http://www.plantuml.com/plantuml')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    plantuml_server.processes_file(puml_path, outfile=output_dir)
    file_name = os.path.splitext(os.path.basename(puml_path))[0] + '.png'
    return os.path.join(output_dir, file_name)


def main():
    parser = argparse.ArgumentParser(
        description='Convierte un archivo DBML o SQL a PlantUML y opcionalmente renderiza el ERD.',
    )
    parser.add_argument('input_file', help='Archivo .dbml o .sql de entrada')
    parser.add_argument('--output', '-o', help='Archivo de salida .puml')
    parser.add_argument('--render', action='store_true', help='Renderiza el .puml a PNG usando PlantUML')
    parser.add_argument('--outdir', default='out', help='Directorio de salida para la imagen PNG renderizada')
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f'Error: El archivo {args.input_file} no existe.')
        return

    with open(args.input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if is_dbml(content):
        tables, relationships = parse_dbml(content)
    else:
        tables, relationships = parse_sql(content)

    if not tables:
        print('No se encontraron tablas válidas en el archivo.')
        return

    output_path = args.output or os.path.splitext(args.input_file)[0] + '.puml'
    save_puml(output_path, build_plantuml(tables, relationships))
    print(f'PlantUML generado: {output_path}')

    if args.render:
        png_path = render_puml(output_path, args.outdir)
        print(f'Diagrama renderizado: {png_path}')


if __name__ == '__main__':
    main()
