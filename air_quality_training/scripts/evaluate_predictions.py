# evaluate_predictions.py
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate(pred_csv):
    df = pd.read_csv(pred_csv, index_col="datetime", parse_dates=True)
    y_true = df["y_true"]
    y_pred = df["y_pred"]
    mae = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred, squared=False)
    r2 = r2_score(y_true, y_pred)
    print("MAE:", mae, "RMSE:", rmse, "R2:", r2)

    # Gráfica
    plt.figure(figsize=(10, 5))
    plt.plot(y_true, label="Real")
    plt.plot(y_pred, label="Predicho")
    plt.legend()
    plt.title("Predicción vs Real de PM2.5")
    plt.show()

if __name__ == "__main__":
    evaluate("models/predictions_pm25.csv")
