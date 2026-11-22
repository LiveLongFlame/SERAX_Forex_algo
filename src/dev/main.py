import asyncio
import logging
import os
import sys
from pathlib import Path

asyncio.set_event_loop(asyncio.new_event_loop())

from ib_insync import Forex, IB, util

from live_model import LiveForexModels


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "model_output"
LIVE_DATA_DIR = DATA_DIR / "live"

IB_HOST = os.getenv("IB_HOST", "127.0.0.1")
IB_PORT = int(os.getenv("IB_PORT", "4002"))
IB_CLIENT_ID = int(os.getenv("IB_CLIENT_ID", "17"))
HISTORY_DURATION = "2 D"
RETRAIN_INTERVAL_SECONDS = 24 * 60 * 60
PAIRS = ("EUR_USD", "AUD_USD")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "WARNING").upper(),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("forex-live-model")


class TerminalDashboard:
    COLORS = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "white": "\033[97m",
        "cyan": "\033[96m",
        "muted": "\033[90m",
        "bold": "\033[1m",
        "reset": "\033[0m",
    }

    def __init__(self) -> None:
        self._use_color = sys.stdout.isatty()
        self._predictions = {}
        self._status = "Connecting to IBKR..."
        self._details = []

    def set_status(self, status: str) -> None:
        self._status = status
        self.render()

    def set_details(self, *details: str) -> None:
        self._details = list(details)
        self.render()

    def update(self, pair: str, prediction: dict, price: float) -> None:
        self._predictions[pair] = {
            **prediction,
            "price": price,
        }
        self.render()

    def _color(self, name: str) -> str:
        return self.COLORS[name] if self._use_color else ""

    def _probability(self, label: str, value: float, color: str) -> str:
        filled = round(value * 10)
        bar = "#" * filled + "-" * (10 - filled)
        return (
            f"{self._color(color)}{label:<8} {bar} {value * 100:5.1f}%"
            f"{self._color('reset')}"
        )

    def render(self) -> None:
        reset = self._color("reset")
        bold = self._color("bold")
        cyan = self._color("cyan")
        muted = self._color("muted")
        width = 88
        rows = [
            f"{bold}{cyan}  SERAX  /  FOREX PROBABILITY MONITOR{reset}",
            f"{muted}  {self._status:<84}{reset}",
            f"{'=' * width}",
        ]

        for pair in PAIRS:
            row = self._predictions.get(pair)
            display_pair = pair.replace("_", "/")
            if row is None:
                rows.extend(
                    [
                        f"  {bold}{display_pair:<10}{reset} Waiting for completed bars...",
                        f"  {'-' * (width - 2)}",
                    ]
                )
                continue

            probabilities = {
                "decrease": row["probability_decrease"],
                "neutral": row["probability_neutral"],
                "increase": row["probability_increase"],
            }
            direction = max(probabilities, key=probabilities.get)
            direction_color = {
                "decrease": "red",
                "neutral": "yellow",
                "increase": "green",
            }[direction]
            timestamp = pd_timestamp(row["timestamp"])
            rows.extend(
                [
                    (
                        f"  {bold}{display_pair:<10}{reset} "
                        f"Price {row['price']:.5f}   "
                        f"Outlook {self._color(direction_color)}"
                        f"{direction.upper():<8}{reset} "
                        f"{muted}{timestamp}{reset}"
                    ),
                    "  "
                    + "   ".join(
                        (
                            self._probability("DECREASE", probabilities["decrease"], "red"),
                            self._probability("NEUTRAL", probabilities["neutral"], "yellow"),
                            self._probability("INCREASE", probabilities["increase"], "green"),
                        )
                    ),
                    f"  {'-' * (width - 2)}",
                ]
            )

        if self._details:
            rows.extend([f"{'=' * width}", *[f"  {line}" for line in self._details]])
        else:
            rows.append(f"{muted}  Ctrl+C to stop{reset}")
        if self._use_color:
            sys.stdout.write("\033[2J\033[H")
        sys.stdout.write("\n".join(rows) + "\n")
        sys.stdout.flush()


def pd_timestamp(value: str) -> str:
    return value.replace("T", " ")[:19] + " UTC"


async def retrain_daily(models: LiveForexModels) -> None:
    while True:
        try:
            results = await asyncio.to_thread(models.retrain_all)
        except (OSError, ValueError, KeyError, TypeError):
            logger.exception(
                "Daily retraining failed for at least one pair; "
                "any completed model refresh remains active"
            )
        else:
            for pair, row_count in results.items():
                logger.info("%s model retrained using %s matured rows", pair, row_count)

        await asyncio.sleep(RETRAIN_INTERVAL_SECONDS)


def main() -> None:
    models = LiveForexModels(
        model_dir=MODEL_DIR,
        data_dir=DATA_DIR,
        live_data_dir=LIVE_DATA_DIR,
    )
    dashboard = TerminalDashboard()
    ib = IB()
    dashboard.set_status(f"Connecting to IBKR  |  {IB_HOST}:{IB_PORT}")
    try:
        ib.connect(IB_HOST, IB_PORT, clientId=IB_CLIENT_ID, timeout=10)
    except KeyboardInterrupt:
        dashboard.set_status("Connection cancelled")
        dashboard.set_details("Startup was stopped with Ctrl+C.")
        return
    except (OSError, asyncio.TimeoutError, TimeoutError) as error:
        dashboard.set_status("Could not connect to IBKR")
        dashboard.set_details(
            f"{type(error).__name__}: {error}",
            "Check that TWS or IB Gateway is running and API access is enabled.",
            f"Current endpoint: {IB_HOST}:{IB_PORT} (paper Gateway is commonly 4002).",
        )
        return

    dashboard.set_status(f"IBKR connected  |  {IB_HOST}:{IB_PORT}  |  1m MIDPOINT  |  15m forecast")

    try:
        for pair in PAIRS:
            contract = Forex(pair.replace("_", ""))
            qualified = ib.qualifyContracts(contract)
            if not qualified:
                raise RuntimeError(f"IBKR could not qualify the {pair} Forex contract")

            bars = ib.reqHistoricalData(
                qualified[0],
                endDateTime="",
                durationStr=HISTORY_DURATION,
                barSizeSetting="1 min",
                whatToShow="MIDPOINT",
                useRTH=False,
                formatDate=2,
                keepUpToDate=True,
            )
            if len(bars) < 70:
                raise RuntimeError(
                    f"IBKR returned only {len(bars)} bars for {pair}; "
                    "need at least 70 recent one-minute bars"
                )

            # With keepUpToDate, the newest bar is still forming; only use completed bars.
            closed_bars = util.df(bars[:-1])
            models.seed_live_cache(pair, closed_bars)
            show_prediction(dashboard, models, pair, closed_bars)

            def on_bar_update(updated_bars, has_new_bar, current_pair=pair):
                if not has_new_bar or len(updated_bars) < 2:
                    return

                closed = updated_bars[-2]
                completed = util.df(updated_bars[:-1])
                try:
                    models.append_live_bar(current_pair, closed)
                    show_prediction(dashboard, models, current_pair, completed)
                except (OSError, ValueError, KeyError, TypeError):
                    logger.exception("Unable to process the latest %s bar", current_pair)

            bars.updateEvent += on_bar_update
            logger.info("Streaming %s 1-minute MIDPOINT bars", pair)

        asyncio.get_event_loop().create_task(retrain_daily(models))
        ib.run()
    except KeyboardInterrupt:
        logger.info("Interrupted; disconnecting from IBKR")
    finally:
        if ib.isConnected():
            ib.disconnect()


def show_prediction(
    dashboard: TerminalDashboard,
    models: LiveForexModels,
    pair: str,
    completed_bars,
) -> None:
    prediction = models.predict(pair, completed_bars)
    price = float(completed_bars.iloc[-1]["close"])
    dashboard.update(pair, prediction, price)


if __name__ == "__main__":
    main()
