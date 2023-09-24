import pandas as pd
import pathlib
import os
from loguru import logger


def get_raw_files(project_dir: pathlib.Path):
    dossier = project_dir / "data/raw"

    liste_fichiers = []
    for dossier_actuel, sous_dossiers, fichiers in os.walk(dossier):
        for fichier in fichiers:
            chemin_complet = os.path.join(dossier_actuel, fichier)
            chemin_relatif = os.path.relpath(chemin_complet, project_dir)
            liste_fichiers.append(pathlib.Path(chemin_relatif))

    return liste_fichiers


def load_data(project_dir: pathlib.Path, data_path: str):
    logger.info(f"Processing {data_path}")
    df = pd.read_csv(project_dir / data_path)

    id_cols = [
        colonne for colonne in df.columns if not any(char.isdigit() for char in colonne)
    ]

    df_long = pd.melt(df, id_vars=id_cols, var_name="type_annee", value_name="valeur")

    df_long["annee"] = df_long["type_annee"].str.extract(r"(\d+)").astype(int)
    df_long["type"] = df_long["type_annee"].str.extract(r"([a-zA-Z]+)")[0]
    df_long.drop(columns=["type_annee"], inplace=True)

    df_long = df_long[id_cols + ["type", "annee"]]
    df_pivot = (
        df_long.pivot(index=id_cols + ["annee"], columns="type", values="valeur")
        .reset_index()
        .drop(columns=["type"])
        .sort_values(by=id_cols + ["annee"])
    )

    df_long.to_csv(project_dir / "data/interim/" / f"{data_path.name}", index=False)


if __name__ == "__main__":
    project_dir = pathlib.Path().resolve()

    files = get_raw_files(project_dir=project_dir)

    for file in files:
        load_data(project_dir, data_path=file)
