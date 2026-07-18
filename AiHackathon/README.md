# TxLINE + IA Marcia Sensitiva

Aplicação para análise esportiva em tempo real, com foco em acompanhar movimentos de odds e identificar tendências durante as partidas.

## Objetivo

O objetivo do app é fornecer análise em tempo real durante o jogo, projetando tendências e possíveis cenários para o decorrer da partida.

## O que a aplicação faz

- acompanha eventos e odds em tempo real;
- identifica variações relevantes no mercado;
- ajuda a entender mudanças de momentum e possíveis oportunidades;
- exibe insights gerados com apoio de análise inteligente;
- organiza jogos em categorias como ao vivo, futuros e finalizados.

## Funcionalidades principais

- varredura do mercado para detectar oportunidades;
- visualização da evolução das odds ao longo do tempo;
- timeline dos eventos da partida;
- análise de contexto com apoio de IA;
- interface simples e interativa em Streamlit.

## Como executar

1. Entre na pasta do projeto:
   ```bash
   cd AiHackathon
   ```

2. Instale as dependências necessárias:
   ```bash
   pip install streamlit pandas plotly
   ```

3. Inicie a aplicação:
   ```bash
   streamlit run app.py
   ```

## Estrutura do projeto

- app.py: interface principal da aplicação;
- ai_analyst.py: lógica de análise com apoio de IA;
- data_processor.py: processamento dos dados das odds;
- database.py: persistência dos dados;
- txline_client.py: integração com a API/serviço de dados;
- worldcup*.json: arquivos com dados de partidas e fixtures.

## Observação

A aplicação é voltada para suporte de análise e acompanhamento durante os jogos, oferecendo uma visão mais dinâmica sobre o comportamento do mercado e possíveis cenários em evolução.
