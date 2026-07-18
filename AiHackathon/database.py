import json
import sqlite3
from pathlib import Path
from typing import Any
import pandas as pd

DB_PATH = Path(__file__).resolve().parent / "txline.db"


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(str(DB_PATH))


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS odds_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fixture_id INTEGER NOT NULL,
            message_id TEXT,
            bookmaker TEXT,
            bookmaker_id INTEGER,
            super_odds_type TEXT,
            market_type TEXT,
            market_parameters TEXT,
            market_period TEXT,
            price_names TEXT,
            prices TEXT,
            participant INTEGER,
            ts INTEGER,
            timestamp TEXT,
            price_raw INTEGER,
            price_decimal REAL,
            probability REAL,
            implied_probability REAL,
            in_running INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS score_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fixture_id INTEGER NOT NULL,
            ts INTEGER,
            timestamp TEXT,
            event_type TEXT,
            minute INTEGER,
            participant TEXT,
            home_score INTEGER,
            away_score INTEGER,
            payload TEXT
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_odds_fixture_type ON odds_history(fixture_id, super_odds_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_score_fixture ON score_events(fixture_id, ts)")

    conn.commit()
    conn.close()


def save_odds_to_db(fixture_id: int, odds_data: list) -> None:
    if not odds_data:
        return

    records = []

    for odd in odds_data:
        prices = odd.get("Prices") or []
        pct = odd.get("Pct") or []
        price_names = odd.get("PriceNames") or []
        ts = odd.get("Ts")
        
        timestamp = None
        if ts is not None:
            timestamp = pd.to_datetime(ts, unit="ms", utc=True).isoformat()

        super_odds_type = odd.get("SuperOddsType", "")
        
        # Extrai o tipo de mercado base (ex: "1X2" de "1X2_PARTICIPANT_RESULT")
        market_type = super_odds_type.split("_")[0] if super_odds_type else "UNKNOWN"

        for participant, raw_price in enumerate(prices):
            if raw_price is None:
                continue

            odd_decimal = raw_price / 1000.0
            probability = None

            # Tenta pegar do Pct da API
            if participant < len(pct):
                value = pct[participant]
                if value not in ("NA", None, ""):
                    try:
                        probability = float(value)
                    except:
                        probability = None

            # Se não tiver, calcula implicitamente
            if probability is None and odd_decimal > 0:
                probability = (1 / odd_decimal) * 100

            records.append({
                "fixture_id": fixture_id,
                "message_id": odd.get("MessageId"),
                "bookmaker": odd.get("Bookmaker"),
                "bookmaker_id": odd.get("BookmakerId"),
                "super_odds_type": super_odds_type,
                "market_type": market_type,
                "market_parameters": str(odd.get("MarketParameters")),
                "market_period": odd.get("MarketPeriod"),
                "price_names": json.dumps(price_names) if price_names else None,
                "prices": json.dumps(prices),
                "participant": participant,
                "ts": ts,
                "timestamp": timestamp,
                "price_raw": raw_price,
                "price_decimal": round(odd_decimal, 3),
                "probability": round(probability, 3) if probability else None,
                "implied_probability": round(probability, 3) if probability else None,
                "in_running": int(odd.get("InRunning", False))
            })

    if not records:
        return

    df = pd.DataFrame(records)
    conn = get_connection()
    df.to_sql("odds_history", conn, if_exists="append", index=False)
    conn.close()

    print(f"✅ {len(df)} odds salvas no banco.")


def save_score_events_to_db(fixture_id: int, events: list) -> None:
    if not events:
        return

    records = []

    for event in events:
        ts = event.get("Ts")
        timestamp = pd.to_datetime(ts, unit="ms", utc=True).isoformat() if ts else None
        
        # Extrai informações do evento
        event_type = event.get("Type") or event.get("Action")
        minute = event.get("Minute")
        if minute is None:
            # Tenta extrair do clock se disponível
            clock = event.get("Clock", {})
            seconds = clock.get("Seconds", 0)
            minute = seconds // 60

        records.append({
            "fixture_id": fixture_id,
            "ts": ts,
            "timestamp": timestamp,
            "event_type": event_type,
            "minute": minute,
            "participant": event.get("Participant"),
            "home_score": event.get("HomeScore"),
            "away_score": event.get("AwayScore"),
            "payload": json.dumps(event)
        })

    df = pd.DataFrame(records)
    conn = get_connection()
    df.to_sql("score_events", conn, if_exists="append", index=False)
    conn.close()

    print(f"✅ {len(df)} eventos salvos no banco.")


def get_odds_history(fixture_id: int):
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT * FROM odds_history
        WHERE fixture_id = ?
        ORDER BY ts ASC
    """, conn, params=[fixture_id])
    conn.close()
    return df


def get_market_history(fixture_id: int, market_type: str, participant: int = 0):
    """
    Busca histórico filtrado por mercado.
    Agora busca de forma mais flexível, aceitando variações do nome.
    """
    conn = get_connection()
    
    # Lista de possíveis variações do mercado
    # Se market_type for "1X2", aceita: "1X2", "1X2_PARTICIPANT_RESULT", "MATCHRESULT", etc.
    if market_type == "1X2":
        query = """
            SELECT * FROM odds_history
            WHERE fixture_id = ?
            AND participant = ?
            AND (
                super_odds_type LIKE '%1X2%' 
                OR super_odds_type LIKE '%MATCHRESULT%'
                OR market_type = '1X2'
            )
            ORDER BY ts ASC
        """
        params = [fixture_id, participant]
    else:
        # Para outros mercados, busca exata ou parcial
        query = """
            SELECT * FROM odds_history
            WHERE fixture_id = ?
            AND participant = ?
            AND (
                super_odds_type LIKE ? 
                OR market_type = ?
            )
            ORDER BY ts ASC
        """
        params = [fixture_id, participant, f"%{market_type}%", market_type]
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df


def get_score_timeline(fixture_id: int):
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT minute, event_type, participant, home_score, away_score, timestamp
        FROM score_events
        WHERE fixture_id = ?
        ORDER BY ts ASC
    """, conn, params=[fixture_id])
    conn.close()
    return df