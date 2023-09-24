import pandas as pd
from loguru import logger
import pathlib

project_dir = pathlib.Path().resolve().parents[0]
file = "cspcommunes.csv"
other_file = "diplomesdepartements.csv"
df = pd.read_csv(project_dir / "data/interim" / file)
dt = pd.read_csv(project_dir / "data/interim" / other_file)

pd.merge(df, dt, on=["dep", "nomdep", "annee"], how="left")
