import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")


class AIAnalyst:
    def __init__(self):
        self.data_dir = Path(__file__).resolve().parent
        self.llm = self._create_llm()
        self.worldcup_data = self._load_json("worldcup.json")
        self.worldcup_groups = self._load_json("worldcup.groups.json")
        self.worldcup_qualis = self._load_json("worldcup.quali_playoffs.json")

    def _create_llm(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY não encontrado. Verifique seu .env.")

        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            api_key=api_key,
        )

    def _build_timeline(self, timeline_events):
        if not timeline_events or len(timeline_events) == 0:
            return "Nenhum evento registrado no jogo."

        linhas = []
        for event in timeline_events:
            minuto = event.get("minute", "?")
            tipo = event.get("event_type", "Evento")
            participant = event.get("participant", "")
            linhas.append(f"{minuto}' - {tipo} ({participant})")

        return "\n".join(linhas[-10:])  # Últimos 10 eventos

    def _load_json(self, filename):
        path = self.data_dir / filename
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return {}

    def generate_ai_insight(self, analysis, home_team, away_team, timeline_events=None):
        if analysis.get("status") != "success":
            return f"⚠️ {analysis.get('message', 'Dados insuficientes.')}"

        timeline = self._build_timeline(timeline_events)

        prompt = f"""
Você é um trader profissional especializado em mercados esportivos e Smart Money.

Analise o jogo: {home_team} x {away_team}

DADOS DO MERCADO:
- Odd Inicial: {analysis['primeira_odd']} (Prob: {analysis['primeira_prob_pct']}%)
- Odd Atual: {analysis['ultima_odd']} (Prob: {analysis['ultima_prob_pct']}%)
- Variação: {analysis['variacao_pct']}%
- Volatilidade: {analysis['volatilidade']}
- Momentum: {analysis['momentum']}
- Velocidade: {analysis['velocidade']}
- Smart Money Score: {analysis['smart_money_score']}/100
- Confiança: {analysis['confianca']}
- Tendência: {analysis['tendencia']}
- Amplitude: {analysis['amplitude']}
- Z-Score: {analysis['z_score']}

TIMELINE DE EVENTOS:
{timeline}

INSTRUÇÕES:
1. Se a odd CAIU (variação negativa): explique que houve entrada de dinheiro/confiança nesse lado
2. Se a odd SUBIU (variação positiva): explique que houve perda de confiança/saída de dinheiro
3. Se houver eventos na timeline, CORRELACIONE com a mudança das odds
4. Se NÃO houver eventos, foque na análise técnica do mercado (volatilidade, momentum)
5. Use linguagem profissional de trader
6. Máximo 3 parágrafos curtos
7. Responda em português
"""

        try:
            resposta = self.llm.invoke([
                SystemMessage(content="Você é um analista quantitativo especializado em apostas esportivas. Seja objetivo e baseado em dados."),
                HumanMessage(content=prompt)
            ])
            return resposta.content
        except Exception as e:
            return f"Erro na IA: {str(e)}. Verifique sua GROQ_API_KEY."


# Instância global
analyst = AIAnalyst()


def generate_ai_insight(analysis, home_team, away_team, timeline_events=None):
    return analyst.generate_ai_insight(analysis, home_team, away_team, timeline_events)