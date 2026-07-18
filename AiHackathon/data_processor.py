import pandas as pd
import numpy as np


def analyze_odds_movement(df, market_type, participant_idx=0):
    if df.empty:
        return {
            "status": "error",
            "message": "Sem histórico."
        }

    df = df.copy()
    
    # Filtro mercado
    if "market_type" in df.columns:
        df = df[df["market_type"] == market_type]
    
    # Filtro participante
    if "participant" in df.columns:
        df = df[df["participant"] == participant_idx]

    if len(df) < 3:
        return {
            "status": "error",
            "message": "Poucos registros."
        }

    # Ordenação - corrigido para aceitar ambos os nomes de coluna
    if "ts" in df.columns:
        df = df.sort_values("ts")
    elif "timestamp" in df.columns:
        df["timestamp_dt"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp_dt")

    odd = df["price_decimal"]

    primeira = odd.iloc[0]
    ultima = odd.iloc[-1]

    prob_inicial = (1 / primeira) * 100 if primeira > 0 else 0
    prob_final = (1 / ultima) * 100 if ultima > 0 else 0

    variacao_pct = ((ultima - primeira) / primeira) * 100 if primeira > 0 else 0

    volatilidade = odd.std()
    media = odd.mean()

    media_movel = odd.rolling(10, min_periods=1).mean()

    momentum = odd.diff().mean()
    velocidade = abs(odd.diff()).mean()

    maximo = odd.max()
    minimo = odd.min()
    amplitude = maximo - minimo

    if odd.std() > 0:
        z_score = (ultima - media) / odd.std()
    else:
        z_score = 0

    if variacao_pct <= -5:
        tendencia = "Entrada forte de dinheiro"
    elif variacao_pct <= -2:
        tendencia = "Pressão compradora"
    elif variacao_pct >= 5:
        tendencia = "Saída forte de dinheiro"
    elif variacao_pct >= 2:
        tendencia = "Pressão vendedora"
    else:
        tendencia = "Mercado estável"

    # Smart Money Score
    score = 0
    score += min(abs(variacao_pct) * 5, 40)
    score += min(volatilidade * 100, 20)
    score += min(abs(z_score) * 10, 20)
    score += min(velocidade * 100, 20)
    score = round(min(score, 100), 1)

    if score >= 85:
        confianca = "Muito Alta"
    elif score >= 70:
        confianca = "Alta"
    elif score >= 50:
        confianca = "Moderada"
    else:
        confianca = "Baixa"

    resultado = {
        "status": "success",
        "market": market_type,
        "participant": participant_idx,
        "amostras": len(df),
        "primeira_odd": round(primeira, 3),
        "ultima_odd": round(ultima, 3),
        "primeira_prob_pct": round(prob_inicial, 2),
        "ultima_prob_pct": round(prob_final, 2),
        "variacao_pct": round(variacao_pct, 2),
        "volatilidade": round(volatilidade, 4),
        "media": round(media, 3),
        "media_movel": round(media_movel.iloc[-1], 3) if not media_movel.empty else 0,
        "momentum": round(momentum, 4),
        "velocidade": round(velocidade, 4),
        "odd_maxima": round(maximo, 3),
        "odd_minima": round(minimo, 3),
        "amplitude": round(amplitude, 3),
        "z_score": round(z_score, 3),
        "tendencia": tendencia,
        "smart_money_score": score,
        "confianca": confianca
    }

    return resultado