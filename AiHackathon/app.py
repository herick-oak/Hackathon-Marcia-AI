import httpx
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone
import time
import httpx._decoders as _decoders

from txline import TxlineClient, ApiToken, GuestJwt
import database as db
import data_processor as processor
from ai_analyst import AIAnalyst

if hasattr(_decoders, "SUPPORTED_DECODERS"):
    _decoders.SUPPORTED_DECODERS.pop("zstd", None)

st.set_page_config(page_title="TxLINE + IA Marcia Sensitiva", page_icon="📈", layout="wide")

# 1. Inicializa o client
client = TxlineClient()

# 2. Pega as chaves dos Secrets
jwt_str = os.getenv("TXLINE_JWT")
api_str = os.getenv("TXLINE_API_TOKEN")

if not jwt_str or not api_str:
    st.error("❌ Erro: TXLINE_JWT ou TXLINE_API_TOKEN não encontrados nos Secrets do Streamlit!")
    st.stop()

# 3. Configura com os objetos corretos da biblioteca (resolve o erro 'str' object has no attribute 'as_str')
client.set_guest_jwt(GuestJwt(jwt_str))
client.set_api_token(ApiToken(api_str))
client.start_guest_session()

ai_analyst = AIAnalyst()

try:
    db.init_db()
except Exception as e:
    st.error(f"Erro ao inicializar DB: {e}")

st.title("📈 TxLINE + IA Marcia Sensitiva")
st.caption("Detecção inteligente de movimentações de odds")

if "fixtures" not in st.session_state:
    st.session_state.fixtures = []
if "opportunities" not in st.session_state:
    st.session_state.opportunities = []

# 4. Carregar fixtures (MANUAL para evitar o bug de Zstandard da biblioteca txline)
if not st.session_state.fixtures:
    with st.spinner("Buscando fixtures..."):
        try:
            # Pega os headers de autenticação que já configuramos
            auth_headers = client.auth_headers(require_api_token=True).to_headers()
            base_url = client.config.api_base
            
            # Faz a requisição MANUALMENTE forçando gzip/identity para evitar o bug do zstd
            with httpx.Client() as http:
                response = http.get(
                    f"{base_url}/fixtures/snapshot",
                    headers={**auth_headers, "Accept-Encoding": "gzip, identity"},
                    timeout=30.0
                )
                response.raise_for_status()
                st.session_state.fixtures = response.json()
                
            st.success(f"✅ {len(st.session_state.fixtures)} fixtures carregados com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao conectar com a API TxLine: {e}")
            st.info("A API de desenvolvimento pode estar instável. Tente recarregar a página.")
            st.stop()

fixtures = st.session_state.fixtures

if not fixtures:
    st.warning("Nenhum fixture encontrado.")
    st.stop()
# Sidebar
st.sidebar.title(" Radar")
scan = st.sidebar.button("📡 Escanear Mercado")

if scan:
    oportunidades = []
    progress = st.sidebar.progress(0)
    total = min(len(fixtures), 15)

    for idx, fixture in enumerate(fixtures[:total]):
        progress.progress((idx + 1) / total)
        fixture_id = fixture["FixtureId"]

        updates = client.odds().live_updates_by_fixture(fixture_id)
        if not updates:
            continue

        db.save_odds_to_db(fixture_id, updates)

        # Tenta diferentes tipos de mercado
        analysis_df = db.get_market_history(fixture_id, "1X2", 0)
        if analysis_df.empty:
            analysis_df = db.get_market_history(fixture_id, "MATCHRESULT", 0)
        
        if analysis_df.empty:
            continue

        analysis = processor.analyze_odds_movement(analysis_df, "1X2", 0)
        
        if analysis["status"] != "success":
            continue

        if abs(analysis["variacao_pct"]) < 3:
            continue

        home = fixture["Participant1"] if fixture["Participant1IsHome"] else fixture["Participant2"]
        away = fixture["Participant2"] if fixture["Participant1IsHome"] else fixture["Participant1"]

        oportunidades.append({
            "fixture_id": fixture_id,
            "home": home,
            "away": away,
            "analysis": analysis
        })

    progress.empty()
    st.session_state.opportunities = oportunidades
    st.rerun()

# Exibir oportunidades
if st.session_state.opportunities:
    st.success(f"🎯 {len(st.session_state.opportunities)} oportunidade(s) detectada(s).")

    for idx, opp in enumerate(st.session_state.opportunities):
        analysis = opp["analysis"]
        titulo = f"{opp['home']} x {opp['away']} • Score {analysis['smart_money_score']}"

        with st.expander(titulo, expanded=(idx == 0)):
            c1, c2, c3 = st.columns(3)
            c1.metric("Variação", f"{analysis['variacao_pct']}%")
            c1.metric("Odd Inicial", analysis["primeira_odd"])
            c1.metric("Odd Atual", analysis["ultima_odd"])
            c2.metric("Volatilidade", analysis["volatilidade"])
            c2.metric("Momentum", analysis["momentum"])
            c3.metric("IA Marcia Sensitiva", analysis["smart_money_score"])
            c3.metric("Confiança", analysis["confianca"])

            history = db.get_market_history(opp["fixture_id"], "1X2", 0)
            if not history.empty:
                history["ts_dt"] = pd.to_datetime(history["ts"], unit="ms")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=history["ts_dt"], y=history["price_decimal"], 
                                        mode="lines", name="Odd"))
                fig.update_layout(height=300, title="Evolução da Odd", 
                                 xaxis_title="Tempo", yaxis_title="Odd")
                st.plotly_chart(fig, use_container_width=True)

            timeline = client.get_score_sequence(opp["fixture_id"])
            if timeline:
                db.save_score_events_to_db(opp["fixture_id"], timeline)
                timeline_df = db.get_score_timeline(opp["fixture_id"])
                if not timeline_df.empty:
                    st.write("### Timeline")
                    st.dataframe(timeline_df, use_container_width=True)

            with st.spinner("Analisando..."):
                insight = ai_analyst.generate_ai_insight(analysis, opp["home"], opp["away"], timeline)
                st.info(insight)

else:
    st.info("Clique em 'Escanear Mercado' para buscar oportunidades.")

# Central de Jogos


now = datetime.now(timezone.utc)
live_games, future_games, finished_games = [], [], []

for fixture in fixtures:
    start = fixture.get("StartTime")
    try:
        if isinstance(start, (int, float)):
            start_dt = datetime.fromtimestamp(start / 1000, tz=timezone.utc)
        else:
            start_dt = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
    except:
        start_dt = now

    home = fixture["Participant1"] if fixture["Participant1IsHome"] else fixture["Participant2"]
    away = fixture["Participant2"] if fixture["Participant1IsHome"] else fixture["Participant1"]

    delta = (start_dt - now).total_seconds() / 3600
    status = "finished" if delta < -3 else ("live" if delta <= 3 else "future")

    game = {"fixture_id": fixture["FixtureId"], "home": home, "away": away, 
            "start": start_dt, "status": status, "fixture": fixture}
    
    if status == "live":
        live_games.append(game)
    elif status == "future":
        future_games.append(game)
    else:
        finished_games.append(game)


def render_game(game):
    fid = game["fixture_id"]
    home, away = game["home"], game["away"]

    col1, col2 = st.columns(2)

    with col1:
        if st.button(" Coletar Odds", key=f"collect_{fid}"):
            with st.spinner("Consultando API..."):
                try:
                    # Tenta buscar updates primeiro
                    updates = client.get_live_odds_updates(fid)
                    
                    if not updates:
                        st.info("Sem updates ao vivo. Tentando snapshot...")
                        updates = client.odds().snapshot(fid)
                    
                    if updates:
                        st.write(f"✅ API retornou {len(updates)} registros!")
                        
                        # Mostra exemplo do que veio
                        st.json(updates[0] if updates else {})
                        
                        # Salva no banco
                        db.save_odds_to_db(fid, updates)
                        
                        # Verifica se salvou
                        verificacao = db.get_odds_history(fid)
                        st.success(f"💾 {len(verificacao)} odds salvas no banco!")
                        
                        st.rerun()
                    else:
                        st.error("❌ API não retornou dados.")
                        
                except Exception as e:
                    st.error(f"Erro: {e}")
                    import traceback
                    st.code(traceback.format_exc())

    # Mostra o que tem no banco
    odds_df = db.get_odds_history(fid)
    if not odds_df.empty:
        st.write(f"📊 {len(odds_df)} odds no banco de dados.")
        
        # Mostra tipos de mercado disponíveis
        if "super_odds_type" in odds_df.columns:
            mercados = odds_df["super_odds_type"].unique()
            st.write(f"**Mercados disponíveis:** {', '.join(mercados[:5])}")
        
        st.dataframe(odds_df[["timestamp", "super_odds_type", "price_decimal", "probability"]].tail(10), 
                    use_container_width=True)
    else:
        st.warning("⚠️ Banco vazio para este jogo.")

    with col2:
        if st.button("🧠 Gerar Análise", key=f"analysis_{fid}"):
            with st.spinner("Processando..."):
                try:
                    # Busca TODOS os dados primeiro para debug
                    todos_dados = db.get_odds_history(fid)
                    st.write(f" Total de registros no banco: {len(todos_dados)}")
                    
                    if todos_dados.empty:
                        st.warning("️ Ainda não existem dados salvos. Colete odds primeiro.")
                        return

                    # Mostra quais mercados existem
                    if "super_odds_type" in todos_dados.columns:
                        mercados_disp = todos_dados["super_odds_type"].unique()
                        st.info(f"Mercados encontrados: {', '.join(mercados_disp)}")

                    # Tenta buscar por 1X2 primeiro
                    history = db.get_market_history(fid, "1X2", 0)
                    
                    # Se não achar, tenta MATCHRESULT
                    if history.empty:
                        st.info("Tentando buscar por MATCHRESULT...")
                        history = db.get_market_history(fid, "MATCHRESULT", 0)
                    
                    # Se ainda não achar, tenta pegar qualquer mercado disponível
                    if history.empty and not todos_dados.empty:
                        st.info("Nenhum mercado 1X2/MATCHRESULT. Usando primeiro mercado disponível...")
                        primeiro_mercado = todos_dados["super_odds_type"].iloc[0]
                        history = db.get_market_history(fid, primeiro_mercado, 0)
                        st.write(f"Usando mercado: {primeiro_mercado}")
                    
                    if history.empty:
                        st.error("❌ Não foi possível encontrar dados válidos para análise.")
                        st.write("Dados brutos disponíveis:")
                        st.dataframe(todos_dados.head())
                        return

                    st.success(f"✅ {len(history)} registros encontrados para análise!")

                    # Processa análise
                    analysis = processor.analyze_odds_movement(history, "1X2", 0)
                    
                    if analysis["status"] != "success":
                        st.warning(analysis["message"])
                        return

                    # Busca timeline
                    timeline = client.get_score_sequence(fid)
                    if timeline:
                        db.save_score_events_to_db(fid, timeline)
                        timeline_df = db.get_score_timeline(fid)
                    else:
                        timeline_df = pd.DataFrame()

                    # Mostra métricas
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("IA Marcia Sensitiva", analysis["smart_money_score"])
                    c2.metric("Variação", f"{analysis['variacao_pct']}%")
                    c3.metric("Volatilidade", analysis["volatilidade"])
                    c4.metric("Confiança", analysis["confianca"])

                    # Gráfico
                    if not history.empty:
                        history["ts_dt"] = pd.to_datetime(history["ts"], unit="ms")
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=history["ts_dt"], y=history["price_decimal"], 
                                                mode="lines", name="Odd"))
                        fig.update_layout(height=300, title="Evolução das Odds")
                        st.plotly_chart(fig, use_container_width=True)

                    # Timeline
                    if not timeline_df.empty:
                        st.write("### Timeline de Eventos")
                        st.dataframe(timeline_df, use_container_width=True)

                    # IA
                    insight = ai_analyst.generate_ai_insight(analysis, home, away, 
                                                            timeline_df.to_dict("records") if not timeline_df.empty else None)
                    st.info(f"💡 {insight}")

                except Exception as e:
                    st.error(f"Erro ao gerar análise: {e}")
                    import traceback
                    st.code(traceback.format_exc())
