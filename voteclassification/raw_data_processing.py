import pandas as pd
import pathlib
import os
from loguru import logger
from omegaconf import OmegaConf
import re


def get_raw_files(project_dir: pathlib.Path):
    dossier = project_dir / "data/raw"

    liste_fichiers = []
    for dossier_actuel, _, fichiers in os.walk(dossier):
        for fichier in fichiers:
            chemin_complet = os.path.join(dossier_actuel, fichier)
            chemin_relatif = os.path.relpath(chemin_complet, project_dir)
            liste_fichiers.append(pathlib.Path(chemin_relatif))

    return liste_fichiers


def process_raw_data(project_dir: pathlib.Path, data_path: str):
    logger.info(f"Processing {data_path}")

    cfg = OmegaConf.load(project_dir / "settings/global.yaml")
    df = pd.read_csv(project_dir / data_path)

    id_cols = [
        colonne for colonne in df.columns if not any(char.isdigit() for char in colonne)
    ]

    annee_pattern = re.compile(r"(\d+)")

    metric_cols = []
    for col in df.columns:
        if not col in id_cols:
            if int(annee_pattern.findall(col)[0]) in cfg.election_years:
                metric_cols.append(col)

    df = df[id_cols + metric_cols]
    df_long = pd.melt(df, id_vars=id_cols, var_name="type_annee", value_name="valeur")

    df_long["annee"] = df_long["type_annee"].str.extract(r"(\d+)").astype(int)
    df_long["type"] = df_long["type_annee"].str.extract(r"([a-zA-Z]+)")[0]

    if "dep" in str(data_path):
        df_long["type"] = df_long["type"] + "_dep"
    else:
        df_long["type"] = df_long["type"]
    df_long.drop(columns=["type_annee"], inplace=True)

    df_pivot = (
        df_long.pivot(index=id_cols + ["annee"], columns="type", values="valeur")
        .reset_index()
        .sort_values(by=id_cols + ["annee"])
    )

    if "paris" in df_pivot.columns:
        df_pivot.drop(columns=["paris"], inplace=True)
    if "pop" not in str(data_path):
        columns_to_drop = [col for col in df_pivot.columns if "pop" in col]
        df_pivot.drop(columns=columns_to_drop, inplace=True)

    df_pivot.to_csv(project_dir / "data/interim" / f"{data_path.name}", index=False)


if __name__ == "__main__":
    project_dir = pathlib.Path().resolve()

    files = get_raw_files(project_dir=project_dir)

    for file in files:
        process_raw_data(project_dir, data_path=file)
