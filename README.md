# 💎 Dashboard Joalheria

Dashboard interativo criado com Gradio para análise de vendas e performance de uma joalheria.

## 📊 Funcionalidades

- **Gráfico de Pizza**: Visualização das vendas por categoria (Anéis, Brincos, Colares, Pulseiras, Relógios)
- **Gráfico de Barras**: Receita mensal dos últimos 12 meses
- **Gráfico de Linha**: Receita acumulada ao longo do tempo
- **Ticket Médio**: Métrica exibida em box destacado
- **NPS (Net Promoter Score)**: Métrica de satisfação do cliente

## 🚀 Como executar

1. Crie e ative o ambiente virtual (se ainda não foi criado):
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o dashboard:
```bash
python main.py
```

**Nota:** Certifique-se de ativar o ambiente virtual antes de executar o dashboard.

3. Acesse o dashboard no navegador:
   - URL local: http://localhost:7860
   - O Gradio também fornecerá uma URL pública se você usar `share=True`

## 📦 Dependências

- gradio >= 4.0.0
- pandas >= 2.0.0
- plotly >= 5.0.0
- numpy >= 1.24.0

## 🔄 Atualização de Dados

O dashboard possui um botão "Atualizar Dashboard" que regenera os dados de exemplo. Em uma implementação real, você pode conectar este botão à sua fonte de dados (banco de dados, API, arquivo CSV, etc.).

## 📝 Notas

- Os dados atuais são de exemplo gerados aleatoriamente
- Para usar dados reais, modifique a função `gerar_dados_exemplo()` para ler de sua fonte de dados
