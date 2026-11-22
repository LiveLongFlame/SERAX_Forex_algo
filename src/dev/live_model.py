import copy
import logging
import os
import threading
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


LOGGER = logging.getLogger("forex-live-model")
PAIRS = ("EUR_USD", "AUD_USD")
LABEL_NAMES = {-1: "decrease", 0: "neutral", 1: "increase"}
RAW_FEATURES = (
    "returns",
    "log_returns",
    "candle_body",
    "candle_range",
    "upper_wick",
    "lower_wick",
    "returns_5m",
    "returns_15m",
    "returns_30m",
    "volatility_15m",
    "volatility_60m",
    "sma_ratio_20",
    "ema_ratio_50",
)
REQUIRED_COLUMNS = ("date", "open", "high", "low", "close")
MIN_TRAINING_ROWS = 1000


class LiveForexModels:
    """Load notebook models, predict live bars, and retrain from matured labels."""

    def __init__(self, model_dir: Path, data_dir: Path, live_data_dir: Path):
        self.model_dir = Path(model_dir)
        self.data_dir = Path(data_dir)
        self.live_data_dir = Path(live_data_dir)
        self.live_data_dir.mkdir(parents=True, exist_ok=True)
        self._model_lock = threading.RLock()
        self._cache_lock = threading.RLock()
        self._models = {}
        self._cache_latest = {}

        for pair in PAIRS:
            model_path = self.model_dir / f"{pair.lower()}_15m_probability.joblib"
            if not model_path.is_file():
                raise FileNotFoundError(
                    f"Model artifact not found: {model_path}. Run the notebook's "
                    "training cells first to create both model artifacts."
                )
            artifact = joblib.load(model_path)
            if artifact.get("pair") != pair or not artifact.get("feature_cols"):
                raise ValueError(f"Unexpected or incomplete model artifact: {model_path}")
            self._models[pair] = artifact

    @staticmethod
    def _normalize_frame(frame: pd.DataFrame, pair: str) -> pd.DataFrame:
        missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
        if missing:
            raise ValueError(f"{pair} market data is missing columns: {missing}")

        df = frame.copy()
        df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
        for column in ("open", "high", "low", "close"):
            df[column] = pd.to_numeric(df[column], errors="coerce")
        if "pair" in df.columns:
            df = df.loc[df["pair"].eq(pair)].copy()
        else:
            df["pair"] = pair
        df = df.dropna(subset=list(REQUIRED_COLUMNS))
        df = df[(df[["open", "high", "low", "close"]] > 0).all(axis=1)]

        valid_ohlc = (
            (df["high"] >= df[["open", "close", "low"]].max(axis=1))
            & (df["low"] <= df[["open", "close", "high"]].min(axis=1))
        )
        return (
            df.loc[valid_ohlc]
            .drop_duplicates(subset=["pair", "date"], keep="last")
            .sort_values(["pair", "date"])
            .reset_index(drop=True)
        )

    @classmethod
    def _engineer_features(cls, frame: pd.DataFrame, pair: str) -> pd.DataFrame:
        df = cls._normalize_frame(frame, pair)
        grouped_close = df.groupby("pair")["close"]

        df["returns"] = grouped_close.pct_change()
        df["log_returns"] = np.log(df["close"] / grouped_close.shift(1))
        df["candle_body"] = df["close"] - df["open"]
        df["candle_range"] = df["high"] - df["low"]
        df["upper_wick"] = df["high"] - df[["open", "close"]].max(axis=1)
        df["lower_wick"] = df[["open", "close"]].min(axis=1) - df["low"]

        for period in (5, 15, 30):
            df[f"returns_{period}m"] = grouped_close.pct_change(period)

        grouped_log_return = df.groupby("pair")["log_returns"]
        df["volatility_15m"] = grouped_log_return.transform(
            lambda values: values.rolling(15).std()
        )
        df["volatility_60m"] = grouped_log_return.transform(
            lambda values: values.rolling(60).std()
        )
        df["sma_ratio_20"] = (
            df["close"]
            / grouped_close.transform(lambda values: values.rolling(20).mean())
            - 1
        )
        df["ema_ratio_50"] = (
            df["close"]
            / grouped_close.transform(
                lambda values: values.ewm(span=50, adjust=False).mean()
            )
            - 1
        )

        for column in RAW_FEATURES:
            df[f"{column}_past"] = df.groupby("pair")[column].shift(1)
        df["lag_return_5"] = grouped_log_return.shift(5)
        df["lag_return_15"] = grouped_log_return.shift(15)

        return df.replace([np.inf, -np.inf], np.nan)

    def predict(self, pair: str, completed_bars: pd.DataFrame) -> dict:
        artifact = self._get_artifact(pair)
        features = self._engineer_features(completed_bars, pair)
        feature_cols = artifact["feature_cols"]
        missing = [column for column in feature_cols if column not in features.columns]
        if missing:
            raise ValueError(f"Model expects unsupported {pair} features: {missing}")

        usable = features.dropna(subset=feature_cols)
        if usable.empty:
            raise ValueError(f"Not enough completed bars to calculate {pair} features")

        row = usable.iloc[[-1]]
        probabilities = artifact["model"].predict_proba(row[feature_cols])[0]
        result = {
            "timestamp": row.iloc[0]["date"].isoformat(),
            "probability_decrease": 0.0,
            "probability_neutral": 0.0,
            "probability_increase": 0.0,
        }
        for label, probability in zip(artifact["model"].classes_, probabilities):
            result[f"probability_{LABEL_NAMES[int(label)]}"] = float(probability)
        return result

    def seed_live_cache(self, pair: str, bars: pd.DataFrame) -> None:
        cache_path = self._cache_path(pair)
        normalized = self._normalize_frame(bars, pair)
        with self._cache_lock:
            if cache_path.is_file():
                existing = self._normalize_frame(pd.read_csv(cache_path), pair)
                normalized = pd.concat([existing, normalized], ignore_index=True)
                normalized = self._normalize_frame(normalized, pair)

            if not normalized.empty:
                temporary_path = cache_path.with_suffix(".csv.tmp")
                try:
                    normalized.to_csv(temporary_path, index=False)
                    os.replace(temporary_path, cache_path)
                finally:
                    if temporary_path.exists():
                        temporary_path.unlink()
                self._cache_latest[pair] = normalized["date"].max()
            else:
                self._cache_latest[pair] = pd.NaT

    def append_live_bar(self, pair: str, bar) -> None:
        row = pd.DataFrame(
            [
                {
                    "date": bar.date,
                    "open": bar.open,
                    "high": bar.high,
                    "low": bar.low,
                    "close": bar.close,
                }
            ]
        )
        normalized = self._normalize_frame(row, pair)
        if normalized.empty:
            raise ValueError(f"IBKR delivered an invalid {pair} bar")

        timestamp = normalized.iloc[0]["date"]
        cache_path = self._cache_path(pair)
        with self._cache_lock:
            latest = self._cache_latest.get(pair, pd.NaT)
            if pd.notna(latest) and timestamp <= latest:
                return

            normalized.to_csv(
                cache_path,
                mode="a",
                header=not cache_path.is_file(),
                index=False,
            )
            self._cache_latest[pair] = timestamp

    def retrain_all(self) -> dict:
        return {pair: self.retrain_pair(pair) for pair in PAIRS}

    def retrain_pair(self, pair: str) -> int:
        artifact = self._get_artifact(pair)
        training_data = self._load_training_data(pair)
        features = self._engineer_features(training_data, pair)

        future_close = features.groupby("pair")["close"].shift(-15)
        features["future_return_15m"] = future_close / features["close"] - 1
        neutral_threshold = float(artifact["neutral_bps"]) / 10000.0
        features["target"] = np.select(
            [
                features["future_return_15m"] > neutral_threshold,
                features["future_return_15m"] < -neutral_threshold,
            ],
            [1, -1],
            default=0,
        )

        feature_cols = artifact["feature_cols"]
        usable = features.dropna(
            subset=feature_cols + ["future_return_15m"]
        )
        if len(usable) < MIN_TRAINING_ROWS:
            raise ValueError(
                f"Only {len(usable)} matured rows available to retrain {pair}; "
                f"need at least {MIN_TRAINING_ROWS}"
            )

        labels = usable["target"].astype(int)
        if labels.nunique() < 2:
            raise ValueError(f"Retraining data for {pair} contains fewer than 2 classes")

        with self._model_lock:
            current_artifact = self._models[pair]
            model = copy.deepcopy(current_artifact["model"])
        model.fit(usable[feature_cols], labels)

        updated_artifact = dict(artifact)
        updated_artifact["model"] = model
        updated_artifact["classes"] = sorted(model.classes_.tolist())
        updated_artifact["retrained_at_utc"] = pd.Timestamp.now(tz="UTC").isoformat()
        updated_artifact["retraining_rows"] = int(len(usable))

        model_path = self._model_path(pair)
        temporary_path = model_path.with_suffix(".joblib.tmp")
        try:
            joblib.dump(updated_artifact, temporary_path)
            os.replace(temporary_path, model_path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()

        with self._model_lock:
            self._models[pair] = updated_artifact
        LOGGER.info("Retrained %s model using %s matured rows", pair, len(usable))
        return len(usable)

    def _load_training_data(self, pair: str) -> pd.DataFrame:
        history_path = self.data_dir / f"combined_{pair.lower()}.csv"
        if not history_path.is_file():
            raise FileNotFoundError(f"Historical training data not found: {history_path}")

        history = pd.read_csv(history_path)
        live_path = self._cache_path(pair)
        with self._cache_lock:
            if live_path.is_file():
                live = pd.read_csv(live_path)
                history = pd.concat([history, live], ignore_index=True)
        return self._normalize_frame(history, pair)

    def _get_artifact(self, pair: str) -> dict:
        if pair not in self._models:
            raise ValueError(f"Unsupported currency pair: {pair}")
        with self._model_lock:
            return self._models[pair]

    def _model_path(self, pair: str) -> Path:
        return self.model_dir / f"{pair.lower()}_15m_probability.joblib"

    def _cache_path(self, pair: str) -> Path:
        if pair not in PAIRS:
            raise ValueError(f"Unsupported currency pair: {pair}")
        return self.live_data_dir / f"{pair.lower()}_live.csv"
