"""Sube sample-docs/ al bucket de documentos, una carpeta por materia.

Cada archivo queda en `<Materia>/<archivo>` junto con su `<archivo>.metadata.json`,
que la Knowledge Base indexa para poder filtrar la búsqueda por materia.
Sincroniza con --delete: lo que no está en sample-docs/ se borra del bucket.

Uso: python3 scripts/seed.py <bucket>
"""

import json
import pathlib
import subprocess
import sys
import tempfile

SAMPLE_DOCS = pathlib.Path(__file__).resolve().parent.parent / "sample-docs"

# Nombre de cada carpeta tal como se muestra en la app.
MATERIAS = {
    "cloud-computing": "Cloud Computing",
    "modelos-de-negocio": "Modelos de Negocio",
    "modelos-formales": "Modelos Formales",
    "teoria-computacion": "Teoría de la Computación",
}

METADATA_SUFFIX = ".metadata.json"


def main(bucket):
    with tempfile.TemporaryDirectory() as staging:
        staging = pathlib.Path(staging)
        for folder in sorted(p for p in SAMPLE_DOCS.iterdir() if p.is_dir()):
            materia = MATERIAS.get(folder.name, folder.name.replace("-", " ").title())
            target = staging / materia
            target.mkdir()
            for doc in sorted(folder.iterdir()):
                if not doc.is_file() or doc.name.endswith(METADATA_SUFFIX) or doc.name.startswith("."):
                    continue
                (target / doc.name).symlink_to(doc)
                (target / (doc.name + METADATA_SUFFIX)).write_text(
                    json.dumps({"metadataAttributes": {"materia": materia}}, ensure_ascii=False)
                )
            print(f"{materia}: {sum(1 for p in target.iterdir() if not p.name.endswith(METADATA_SUFFIX))} documentos")

        subprocess.run(["aws", "s3", "sync", f"{staging}/", f"s3://{bucket}/", "--delete", "--follow-symlinks"], check=True)


if __name__ == "__main__":
    main(sys.argv[1])
