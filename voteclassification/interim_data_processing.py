import pandas as pd
from loguru import logger
import pathlib
import os
from omegaconf import OmegaConf


def process_interim_data(project_dir):
    files = os.listdir(project_dir / "data/interim")
    liste_df = [pd.read_csv(project_dir / "data/interim" / file) for file in files]
    result = liste_df[0]

    for i, df in enumerate(liste_df[1:]):
        logger.info(f"Merging file {files[i+1]}")
        if "dep" in files[i + 1]:
            result = pd.merge(result, df, on=["dep", "nomdep", "annee"], how="left")
        elif "commune" in files[i + 1]:
            result = pd.merge(
                result,
                df,
                on=["dep", "nomdep", "codecommune", "nomcommune", "annee"],
                how="left",
            )

    duplicated_columns = [col for col in result.columns if "_y" in col]
    duplicated_columns = duplicated_columns + [
        col for col in result.columns if "_x" in col
    ]

    result = result[[col for col in result.columns if col not in duplicated_columns]]
    id_cols = [
        "dep",
        "nomdep",
        "codecommune",
        "nomcommune",
        "annee",
        "codeagglo",
        "nomagglo",
        "nomreg",
    ]
    cfg = OmegaConf.load(project_dir / "settings/global.yaml")
    result = result[id_cols + cfg.features]

    for y in list(result.annee.unique()):
        logger.info(f"Writing file for year {y}")
        df = result.query("annee == @y")
        df.to_csv(project_dir / f"data/processed/processed_{y}.csv")

    # next rounds
    df = result[[col for col in result.columns if col not in id_cols]]


if __name__ == "__main__":
    project_dir = pathlib.Path().resolve()

    result = process_interim_data(project_dir=project_dir)
