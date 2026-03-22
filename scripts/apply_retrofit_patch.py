from pathlib import Path

import yaml


def patch_docs():
    patch_dir = Path("data/retrofit-patches")
    docs_dir = Path("docs/research")

    patches = list(patch_dir.glob("*.yml"))

    for patch_path in sorted(patches):
        doc_filename = patch_path.name.replace(".yml", ".md")
        doc_path = docs_dir / doc_filename

        if not doc_path.exists():
            print(f"Warning: Document {doc_path} does not exist.")
            continue

        print(f"Applying {patch_path.name}...")
        with open(patch_path, "r") as f:
            try:
                patch_data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Error parsing {patch_path}: {e}")
                continue

        recs = patch_data.get("recommendations", [])
        if not recs:
            continue

        # Strip _match_note and _confidence
        clean_recs = []
        for rec in recs:
            clean_rec = {k: v for k, v in rec.items() if k not in ["_match_note", "_confidence"]}
            clean_recs.append(clean_rec)

        # Read doc
        content = doc_path.read_text()

        # Split frontmatter
        parts = content.split("---", 2)
        if len(parts) < 3:
            print(f"Error: {doc_path} has malformed frontmatter.")
            continue

        frontmatter_text = parts[1]

        try:
            frontmatter = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as e:
            print(f"Error parsing frontmatter in {doc_path}: {e}")
            print("Frontmatter content:")
            print(frontmatter_text)
            continue

        frontmatter["recommendations"] = clean_recs

        # Re-encode frontmatter
        new_frontmatter_text = yaml.dump(frontmatter, sort_keys=False, allow_unicode=True)
        new_content = f"---\n{new_frontmatter_text}---" + "".join(parts[2:])

        doc_path.write_text(new_content)
        print(f"Patched {doc_filename}")


if __name__ == "__main__":
    patch_docs()
