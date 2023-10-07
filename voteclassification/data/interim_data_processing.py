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

    df = result[[col for col in result.columns if col not in duplicated_columns]]
    id_cols = [
        "dep",
        "nomdep",
        "codecommune",
        "nomcommune",
        "annee",
    ]
    cfg = OmegaConf.load(project_dir / "settings/global.yaml")
    df = df[id_cols + cfg.features]

    # Fill na by interpolation, median computing
    df = df[~df.nomcommune.isna()]
    grouped = df.groupby(["dep", "nomdep", "codecommune", "nomcommune"])
    medians = grouped.median().reset_index()
    df = df.fillna(medians).sort_values(by=["dep", "nomcommune"])
    grouped = df.groupby(["dep", "nomdep", "codecommune", "nomcommune"])
    df = grouped.apply(lambda group: complete_na(group, cfg))
    df = df.reset_index()

    logger.info(f"Writing the whole dataset")

    df.to_csv(project_dir / f"data/processed/processed_all.csv")
    for y in list(df.annee.unique()):
        logger.info(f"Writing file for year {y}")
        df_year = df.query("annee == @y")
        df_year.to_csv(project_dir / f"data/processed/processed_{y}.csv")

    return df


def complete_na(df_grouped: pd.DataFrame, cfg):
    logger.info(
        f"Group name : {df_grouped[['nomdep']].iloc[0,0]} - {df_grouped[['nomcommune']].iloc[0,0]}"
    )
    df_grouped.loc[:, cfg.features] = df_grouped[cfg.features].interpolate(
        direction="both"
    )
    df_grouped = df_grouped.bfill().ffill()

    return df_grouped


if __name__ == "__main__":
    project_dir = pathlib.Path().resolve()

    df = process_interim_data(project_dir=project_dir)
