import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Dados de exemplo para demonstração
def gerar_dados_exemplo():
    """Gera dados de exemplo para o dashboard"""
    # Dados para gráfico de pizza (vendas por categoria)
    categorias = ['Anéis', 'Brincos', 'Colares', 'Pulseiras', 'Relógios']
    vendas = [45000, 32000, 38000, 25000, 40000]
    
    # Dados para receita mensal (últimos 12 meses)
    meses = pd.date_range(end=datetime.now(), periods=12, freq='M')
    receita_mensal = np.random.randint(80000, 150000, 12)
    
    # Receita acumulada
    receita_acumulada = np.cumsum(receita_mensal)
    
    # Ticket médio
    ticket_medio = 1250.50
    
    # NPS (Net Promoter Score)
    nps = 72
    
    return {
        'categorias': categorias,
        'vendas': vendas,
        'meses': meses,
        'receita_mensal': receita_mensal,
        'receita_acumulada': receita_acumulada,
        'ticket_medio': ticket_medio,
        'nps': nps
    }

def criar_grafico_pizza():
    """Cria gráfico de pizza com as vendas por categoria"""
    dados = gerar_dados_exemplo()
    
    fig = go.Figure(data=[go.Pie(
        labels=dados['categorias'],
        values=dados['vendas'],
        hole=0.3,
        marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'])
    )])
    
    fig.update_layout(
        title={
            'text': 'Vendas por Categoria',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        showlegend=True,
        height=400
    )
    
    return fig

def criar_grafico_barras_receita():
    """Cria gráfico de barras com receita mensal"""
    dados = gerar_dados_exemplo()
    
    fig = go.Figure(data=[
        go.Bar(
            x=[mes.strftime('%b/%Y') for mes in dados['meses']],
            y=dados['receita_mensal'],
            marker_color='#4ECDC4',
            text=[f'R$ {val:,.0f}'.replace(',', '.') for val in dados['receita_mensal']],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Receita Mensal',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Mês',
        yaxis_title='Receita (R$)',
        height=400,
        xaxis={'tickangle': -45}
    )
    
    return fig

def criar_grafico_receita_acumulada():
    """Cria gráfico de linha com receita acumulada"""
    dados = gerar_dados_exemplo()
    
    fig = go.Figure(data=[
        go.Scatter(
            x=[mes.strftime('%b/%Y') for mes in dados['meses']],
            y=dados['receita_acumulada'],
            mode='lines+markers',
            line=dict(color='#45B7D1', width=3),
            marker=dict(size=8),
            fill='tonexty',
            fillcolor='rgba(69, 183, 209, 0.2)'
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Receita Acumulada',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Mês',
        yaxis_title='Receita Acumulada (R$)',
        height=400,
        xaxis={'tickangle': -45}
    )
    
    return fig

def atualizar_dashboard():
    """Atualiza todos os componentes do dashboard"""
    dados = gerar_dados_exemplo()
    
    # Criar os gráficos
    grafico_pizza = criar_grafico_pizza()
    grafico_barras = criar_grafico_barras_receita()
    grafico_acumulado = criar_grafico_receita_acumulada()
    
    # Formatar valores
    ticket_medio_formatado = f"R$ {dados['ticket_medio']:,.2f}".replace(',', '.')
    nps_formatado = f"{dados['nps']}"
    
    return (
        grafico_pizza,
        grafico_barras,
        grafico_acumulado,
        ticket_medio_formatado,
        nps_formatado
    )

# Interface Gradio
with gr.Blocks(title="Dashboard Joalheria", theme=gr.themes.Soft()) as dashboard:
    gr.Markdown(
        """
        # 💎 Dashboard Joalheria
        ### Análise de Vendas e Performance
        """
    )
    
    with gr.Row():
        # Box Ticket Médio
        with gr.Column(scale=1):
            ticket_medio_box = gr.Markdown(
                """
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 30px; border-radius: 15px; text-align: center; 
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: white; margin: 0 0 10px 0;">🎫 Ticket Médio</h2>
                    <h1 style="color: white; margin: 0; font-size: 2.5em;" id="ticket-medio">R$ 0,00</h1>
                </div>
                """
            )
        
        # Box NPS
        with gr.Column(scale=1):
            nps_box = gr.Markdown(
                """
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                            padding: 30px; border-radius: 15px; text-align: center; 
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: white; margin: 0 0 10px 0;">⭐ NPS</h2>
                    <h1 style="color: white; margin: 0; font-size: 2.5em;" id="nps">0</h1>
                </div>
                """
            )
    
    with gr.Row():
        # Gráfico de Pizza
        grafico_pizza = gr.Plot(label="Vendas por Categoria")
    
    with gr.Row():
        # Gráfico de Barras - Receita Mensal
        grafico_barras = gr.Plot(label="Receita Mensal")
    
    with gr.Row():
        # Gráfico de Linha - Receita Acumulada
        grafico_acumulado = gr.Plot(label="Receita Acumulada")
    
    # Botão para atualizar
    btn_atualizar = gr.Button("🔄 Atualizar Dashboard", variant="primary", size="lg")
    
    # Atualizar valores dos boxes
    ticket_medio_value = gr.Textbox(visible=False)
    nps_value = gr.Textbox(visible=False)
    
    # Função para atualizar os boxes com valores
    def atualizar_boxes(ticket, nps):
        ticket_html = f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 15px; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: white; margin: 0 0 10px 0;">🎫 Ticket Médio</h2>
            <h1 style="color: white; margin: 0; font-size: 2.5em;">{ticket}</h1>
        </div>
        """
        nps_html = f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 30px; border-radius: 15px; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: white; margin: 0 0 10px 0;">⭐ NPS</h2>
            <h1 style="color: white; margin: 0; font-size: 2.5em;">{nps}</h1>
        </div>
        """
        return ticket_html, nps_html
    
    # Conectar eventos
    btn_atualizar.click(
        fn=atualizar_dashboard,
        outputs=[grafico_pizza, grafico_barras, grafico_acumulado, ticket_medio_value, nps_value]
    ).then(
        fn=atualizar_boxes,
        inputs=[ticket_medio_value, nps_value],
        outputs=[ticket_medio_box, nps_box]
    )
    
    # Carregar dados iniciais
    dashboard.load(
        fn=atualizar_dashboard,
        outputs=[grafico_pizza, grafico_barras, grafico_acumulado, ticket_medio_value, nps_value]
    ).then(
        fn=atualizar_boxes,
        inputs=[ticket_medio_value, nps_value],
        outputs=[ticket_medio_box, nps_box]
    )

if __name__ == "__main__":
    dashboard.launch(share=False, server_name="0.0.0.0", server_port=7860)
