from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import MinMaxScaler
import joblib
from omegaconf import OmegaConf
import pathlib


def train_model(project_dir):
    cfg = OmegaConf.load(project_dir / "settings/global.yaml")
    df = project_dir / "data/processed"

    for y in cfg.elections_years:
        param_grid = {"n_estimators": [10, 25, 50, 75, 100, 125, 150, 175, 200]}
        X_train, Y_train, X_test, Y_test = train_test_split(df, test_size=0.2)

        rf = RandomForestClassifier()
        gridsearch = GridSearchCV(rf, param_grid=param_grid, cv=5, verbose=2)
        gridsearch.fit(X_train, Y_train)

        best_rf = gridsearch.best_estimator_
        model_filename = project_dir / f"data/models/classifier_{y}.pkl"

        joblib.dump(best_rf, model_filename)


if __name__ == "__main__":
    project_dir = pathlib.Path().resolve()

    train_model(project_dir=project_dir)
