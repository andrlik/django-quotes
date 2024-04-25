from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()  # type: ignore[attr-defined]

for path in sorted(Path("src/django_quotes").rglob("*.py")):
    module_path = path.with_suffix("")
    module_package_path = path.relative_to("src").with_suffix("")
    doc_path = path.relative_to("src").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)
    package_parts = tuple(module_package_path.parts)

    if "migrations" not in parts and parts[-1] != "__init__":
        if parts[-1].startswith("_") or parts[-1] == "src":
            continue

        nav[package_parts] = doc_path.as_posix()

        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            indent = ".".join(parts)
            fd.write(f"::: {indent}")

        mkdocs_gen_files.set_edit_path(full_doc_path, Path("../") / path)

with mkdocs_gen_files.open("reference/SUMMARY.txt", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
