import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os

# Caminhos dos arquivos CSV
VENDAS_CSV = 'vendas_joalheria.csv'
GASTOS_CSV = 'gastos_joalheria.csv'

def carregar_dados():
    """Carrega e processa os dados dos CSVs de vendas e gastos"""
    # Verificar se os arquivos existem
    if not os.path.exists(VENDAS_CSV):
        raise FileNotFoundError(f"Arquivo {VENDAS_CSV} não encontrado!")
    if not os.path.exists(GASTOS_CSV):
        raise FileNotFoundError(f"Arquivo {GASTOS_CSV} não encontrado!")
    
    # Ler os CSVs
    df_vendas = pd.read_csv(VENDAS_CSV)
    df_gastos = pd.read_csv(GASTOS_CSV)
    
    # Converter datas para datetime
    df_vendas['data_venda'] = pd.to_datetime(df_vendas['data_venda'])
    df_gastos['data_gasto'] = pd.to_datetime(df_gastos['data_gasto'])
    
    # ========== PROCESSAMENTO DE VENDAS ==========
    # Calcular vendas por categoria (soma do valor_total)
    vendas_por_categoria = df_vendas.groupby('categoria')['valor_total'].sum().sort_values(ascending=False)
    
    # Calcular receita mensal
    df_vendas['ano_mes'] = df_vendas['data_venda'].dt.to_period('M')
    receita_mensal = df_vendas.groupby('ano_mes')['valor_total'].sum().sort_index()
    
    # Calcular receita acumulada
    receita_acumulada = receita_mensal.cumsum()
    
    # Calcular ticket médio (média do valor_total)
    ticket_medio = df_vendas['valor_total'].mean()
    
    # Calcular NPS
    # NPS = % Promotores (9-10) - % Detratores (0-6)
    promotores = len(df_vendas[df_vendas['nps_score'] >= 9])
    detratores = len(df_vendas[df_vendas['nps_score'] <= 6])
    total_respostas = len(df_vendas)
    
    percentual_promotores = (promotores / total_respostas) * 100
    percentual_detratores = (detratores / total_respostas) * 100
    nps = percentual_promotores - percentual_detratores
    
    # ========== PROCESSAMENTO DE GASTOS ==========
    # Calcular gastos mensais
    df_gastos['ano_mes'] = df_gastos['data_gasto'].dt.to_period('M')
    gastos_mensais = df_gastos.groupby('ano_mes')['valor'].sum().sort_index()
    
    # Calcular gastos por categoria
    gastos_por_categoria = df_gastos.groupby('categoria_gasto')['valor'].sum().sort_values(ascending=False)
    
    # Calcular gastos acumulados
    gastos_acumulados = gastos_mensais.cumsum()
    
    # ========== MÉTRICAS FINANCEIRAS ==========
    # Alinhar receita e gastos por mês
    meses_comuns = receita_mensal.index.intersection(gastos_mensais.index)
    
    # Calcular lucro mensal (receita - gastos)
    lucro_mensal = receita_mensal.loc[meses_comuns] - gastos_mensais.loc[meses_comuns]
    
    # Calcular lucro acumulado
    lucro_acumulado = lucro_mensal.cumsum()
    
    # Calcular margem de lucro mensal (%)
    margem_lucro_mensal = (lucro_mensal / receita_mensal.loc[meses_comuns]) * 100
    
    # Calcular totais
    receita_total = receita_mensal.sum()
    gastos_total = gastos_mensais.sum()
    lucro_total = receita_total - gastos_total
    margem_lucro_total = (lucro_total / receita_total) * 100 if receita_total > 0 else 0
    
    # Calcular ROI (Return on Investment)
    # ROI = (Lucro / Gastos) * 100
    roi = (lucro_total / gastos_total) * 100 if gastos_total > 0 else 0
    
    return {
        # Vendas
        'categorias': vendas_por_categoria.index.tolist(),
        'vendas': vendas_por_categoria.values.tolist(),
        'meses': receita_mensal.index.to_timestamp(),
        'receita_mensal': receita_mensal.values.tolist(),
        'receita_acumulada': receita_acumulada.values.tolist(),
        'ticket_medio': ticket_medio,
        'nps': round(nps, 1),
        # Gastos
        'categorias_gastos': gastos_por_categoria.index.tolist(),
        'gastos_categoria': gastos_por_categoria.values.tolist(),
        'gastos_mensais': gastos_mensais.values.tolist(),
        'gastos_acumulados': gastos_acumulados.values.tolist(),
        'meses_gastos': gastos_mensais.index.to_timestamp(),
        # Métricas financeiras
        'lucro_mensal': lucro_mensal.values.tolist(),
        'lucro_acumulado': lucro_acumulado.values.tolist(),
        'margem_lucro_mensal': margem_lucro_mensal.values.tolist(),
        'meses_lucro': meses_comuns.to_timestamp(),
        'receita_total': receita_total,
        'gastos_total': gastos_total,
        'lucro_total': lucro_total,
        'margem_lucro_total': margem_lucro_total,
        'roi': roi
    }

def criar_grafico_pizza():
    """Cria gráfico de pizza com as vendas por categoria"""
    dados = carregar_dados()
    
    # Cores para as categorias
    cores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE']
    
    fig = go.Figure(data=[go.Pie(
        labels=dados['categorias'],
        values=dados['vendas'],
        hole=0.3,
        marker=dict(colors=cores[:len(dados['categorias'])])
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
    dados = carregar_dados()
    
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
    dados = carregar_dados()
    
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

def criar_grafico_gastos_categoria():
    """Cria gráfico de pizza com gastos por categoria"""
    dados = carregar_dados()
    
    cores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']
    
    fig = go.Figure(data=[go.Pie(
        labels=dados['categorias_gastos'],
        values=dados['gastos_categoria'],
        hole=0.3,
        marker=dict(colors=cores[:len(dados['categorias_gastos'])])
    )])
    
    fig.update_layout(
        title={
            'text': 'Gastos por Categoria',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        showlegend=True,
        height=400
    )
    
    return fig

def criar_grafico_receita_vs_gastos():
    """Cria gráfico comparando receita e gastos mensais"""
    dados = carregar_dados()
    
    # Alinhar meses
    meses_receita = [mes.strftime('%b/%Y') for mes in dados['meses']]
    meses_gastos = [mes.strftime('%b/%Y') for mes in dados['meses_gastos']]
    
    fig = go.Figure()
    
    # Adicionar receita
    fig.add_trace(go.Bar(
        x=meses_receita,
        y=dados['receita_mensal'],
        name='Receita',
        marker_color='#4ECDC4'
    ))
    
    # Adicionar gastos
    fig.add_trace(go.Bar(
        x=meses_gastos,
        y=dados['gastos_mensais'],
        name='Gastos',
        marker_color='#FF6B6B'
    ))
    
    fig.update_layout(
        title={
            'text': 'Receita vs Gastos Mensais',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Mês',
        yaxis_title='Valor (R$)',
        barmode='group',
        height=400,
        xaxis={'tickangle': -45},
        legend=dict(x=0.7, y=1)
    )
    
    return fig

def criar_grafico_lucro_mensal():
    """Cria gráfico de barras com lucro mensal"""
    dados = carregar_dados()
    
    cores = ['#FF6B6B' if lucro < 0 else '#4ECDC4' for lucro in dados['lucro_mensal']]
    
    fig = go.Figure(data=[
        go.Bar(
            x=[mes.strftime('%b/%Y') for mes in dados['meses_lucro']],
            y=dados['lucro_mensal'],
            marker_color=cores,
            text=[f'R$ {val:,.0f}'.replace(',', '.') for val in dados['lucro_mensal']],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Lucro Mensal',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Mês',
        yaxis_title='Lucro (R$)',
        height=400,
        xaxis={'tickangle': -45}
    )
    
    # Adicionar linha de referência em zero
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    return fig

def atualizar_dashboard_receita():
    """Atualiza componentes da aba Receita"""
    dados = carregar_dados()
    
    grafico_pizza = criar_grafico_pizza()
    grafico_barras = criar_grafico_barras_receita()
    grafico_acumulado = criar_grafico_receita_acumulada()
    
    ticket_medio_formatado = f"R$ {dados['ticket_medio']:,.2f}".replace(',', '.')
    nps_formatado = f"{dados['nps']}"
    receita_total_formatada = f"R$ {dados['receita_total']:,.2f}".replace(',', '.')
    
    return (
        grafico_pizza,
        grafico_barras,
        grafico_acumulado,
        ticket_medio_formatado,
        nps_formatado,
        receita_total_formatada
    )

def atualizar_dashboard_custos():
    """Atualiza componentes da aba Custos"""
    dados = carregar_dados()
    
    grafico_gastos = criar_grafico_gastos_categoria()
    
    # Criar gráfico de gastos mensais
    fig_gastos_mensais = go.Figure(data=[
        go.Bar(
            x=[mes.strftime('%b/%Y') for mes in dados['meses_gastos']],
            y=dados['gastos_mensais'],
            marker_color='#FF6B6B',
            text=[f'R$ {val:,.0f}'.replace(',', '.') for val in dados['gastos_mensais']],
            textposition='outside'
        )
    ])
    
    fig_gastos_mensais.update_layout(
        title={
            'text': 'Gastos Mensais',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Mês',
        yaxis_title='Gastos (R$)',
        height=400,
        xaxis={'tickangle': -45}
    )
    
    # Criar gráfico de gastos acumulados
    fig_gastos_acumulados = go.Figure(data=[
        go.Scatter(
            x=[mes.strftime('%b/%Y') for mes in dados['meses_gastos']],
            y=dados['gastos_acumulados'],
            mode='lines+markers',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8),
            fill='tonexty',
            fillcolor='rgba(231, 76, 60, 0.2)'
        )
    ])
    
    fig_gastos_acumulados.update_layout(
        title={
            'text': 'Gastos Acumulados',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Mês',
        yaxis_title='Gastos Acumulados (R$)',
        height=400,
        xaxis={'tickangle': -45}
    )
    
    gastos_total_formatado = f"R$ {dados['gastos_total']:,.2f}".replace(',', '.')
    gasto_medio_mensal = dados['gastos_total'] / len(dados['gastos_mensais'])
    gasto_medio_formatado = f"R$ {gasto_medio_mensal:,.2f}".replace(',', '.')
    
    return (
        grafico_gastos,
        fig_gastos_mensais,
        fig_gastos_acumulados,
        gastos_total_formatado,
        gasto_medio_formatado
    )

def atualizar_dashboard_lucro():
    """Atualiza componentes da aba Lucro"""
    dados = carregar_dados()
    
    grafico_lucro = criar_grafico_lucro_mensal()
    grafico_receita_gastos = criar_grafico_receita_vs_gastos()
    
    # Criar gráfico de lucro acumulado
    fig_lucro_acumulado = go.Figure(data=[
        go.Scatter(
            x=[mes.strftime('%b/%Y') for mes in dados['meses_lucro']],
            y=dados['lucro_acumulado'],
            mode='lines+markers',
            line=dict(color='#2ecc71', width=3),
            marker=dict(size=8),
            fill='tonexty',
            fillcolor='rgba(46, 204, 113, 0.2)'
        )
    ])
    
    fig_lucro_acumulado.update_layout(
        title={
            'text': 'Lucro Acumulado',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Mês',
        yaxis_title='Lucro Acumulado (R$)',
        height=400,
        xaxis={'tickangle': -45}
    )
    
    # Adicionar linha de referência em zero
    fig_lucro_acumulado.add_hline(y=0, line_dash="dash", line_color="gray")
    
    lucro_total_formatado = f"R$ {dados['lucro_total']:,.2f}".replace(',', '.')
    margem_formatada = f"{dados['margem_lucro_total']:.1f}%"
    roi_formatado = f"{dados['roi']:.1f}%"
    
    return (
        grafico_lucro,
        grafico_receita_gastos,
        fig_lucro_acumulado,
        lucro_total_formatado,
        margem_formatada,
        roi_formatado
    )

# Interface Gradio com Abas
with gr.Blocks(title="Dashboard Joalheria") as dashboard:
    gr.Markdown(
        """
        # 💎 Dashboard Joalheria
        ### Análise Completa de Vendas, Gastos e Performance Financeira
        """
    )
    
    # Botão para atualizar (comum a todas as abas)
    btn_atualizar = gr.Button("🔄 Atualizar Dashboard", variant="primary", size="lg")
    
    # Criar abas
    with gr.Tabs() as tabs:
        # ========== ABA RECEITA ==========
        with gr.Tab("💰 Receita"):
            gr.Markdown("### 📊 Análise de Receita e Vendas")
            
            # Métricas principais
            with gr.Row():
                ticket_medio_box = gr.Markdown()
                nps_box = gr.Markdown()
                receita_total_box = gr.Markdown()
            
            # Gráficos
            grafico_pizza = gr.Plot(label="Vendas por Categoria")
            grafico_barras_receita = gr.Plot(label="Receita Mensal")
            grafico_acumulado_receita = gr.Plot(label="Receita Acumulada")
            
            # Valores ocultos
            ticket_medio_value = gr.Textbox(visible=False)
            nps_value = gr.Textbox(visible=False)
            receita_total_value = gr.Textbox(visible=False)
        
        # ========== ABA CUSTOS ==========
        with gr.Tab("💸 Custos"):
            gr.Markdown("### 📉 Análise de Custos e Gastos")
            
            # Métricas principais
            with gr.Row():
                gastos_total_box = gr.Markdown()
                gasto_medio_box = gr.Markdown()
            
            # Gráficos
            grafico_gastos_categoria = gr.Plot(label="Gastos por Categoria")
            grafico_gastos_mensais = gr.Plot(label="Gastos Mensais")
            grafico_gastos_acumulados = gr.Plot(label="Gastos Acumulados")
            
            # Valores ocultos
            gastos_total_value = gr.Textbox(visible=False)
            gasto_medio_value = gr.Textbox(visible=False)
        
        # ========== ABA LUCRO ==========
        with gr.Tab("📈 Lucro"):
            gr.Markdown("### 💰 Análise de Lucro e Rentabilidade")
            
            # Métricas principais
            with gr.Row():
                lucro_total_box = gr.Markdown()
                margem_lucro_box = gr.Markdown()
                roi_box = gr.Markdown()
            
            # Gráficos
            grafico_lucro_mensal = gr.Plot(label="Lucro Mensal")
            grafico_receita_vs_gastos = gr.Plot(label="Receita vs Gastos")
            grafico_lucro_acumulado = gr.Plot(label="Lucro Acumulado")
            
            # Valores ocultos
            lucro_total_value = gr.Textbox(visible=False)
            margem_lucro_value = gr.Textbox(visible=False)
            roi_value = gr.Textbox(visible=False)
    
    # Funções para atualizar boxes
    def atualizar_boxes_receita(ticket, nps, receita):
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
        receita_html = f"""
        <div style="background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%); 
                    padding: 30px; border-radius: 15px; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: white; margin: 0 0 10px 0;">💰 Receita Total</h2>
            <h1 style="color: white; margin: 0; font-size: 2.5em;">{receita}</h1>
        </div>
        """
        return ticket_html, nps_html, receita_html
    
    def atualizar_boxes_custos(gastos_total, gasto_medio):
        gastos_html = f"""
        <div style="background: linear-gradient(135deg, #FF6B6B 0%, #C92A2A 100%); 
                    padding: 30px; border-radius: 15px; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: white; margin: 0 0 10px 0;">💸 Gastos Total</h2>
            <h1 style="color: white; margin: 0; font-size: 2.5em;">{gastos_total}</h1>
        </div>
        """
        gasto_medio_html = f"""
        <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); 
                    padding: 30px; border-radius: 15px; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: white; margin: 0 0 10px 0;">📊 Gasto Médio Mensal</h2>
            <h1 style="color: white; margin: 0; font-size: 2.5em;">{gasto_medio}</h1>
        </div>
        """
        return gastos_html, gasto_medio_html
    
    def atualizar_boxes_lucro(lucro, margem, roi):
        # Determinar cor do lucro baseado no sinal
        lucro_valor = lucro.replace("R$ ", "").replace(".", "").replace(",", ".")
        try:
            valor_numerico = float(lucro_valor)
            if valor_numerico >= 0:
                cor_lucro = "#2ecc71"
                cor_fim = "#27ae60"
            else:
                cor_lucro = "#e74c3c"
                cor_fim = "#c0392b"
        except:
            cor_lucro = "#3498db"
            cor_fim = "#2980b9"
        
        lucro_html = f"""
        <div style="background: linear-gradient(135deg, {cor_lucro} 0%, {cor_fim} 100%); 
                    padding: 30px; border-radius: 15px; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: white; margin: 0 0 10px 0;">💰 Lucro Total</h2>
            <h1 style="color: white; margin: 0; font-size: 2.5em;">{lucro}</h1>
        </div>
        """
        margem_html = f"""
        <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); 
                    padding: 30px; border-radius: 15px; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: white; margin: 0 0 10px 0;">📊 Margem de Lucro</h2>
            <h1 style="color: white; margin: 0; font-size: 2.5em;">{margem}</h1>
        </div>
        """
        roi_html = f"""
        <div style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); 
                    padding: 30px; border-radius: 15px; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: white; margin: 0 0 10px 0;">🎯 ROI</h2>
            <h1 style="color: white; margin: 0; font-size: 2.5em;">{roi}</h1>
        </div>
        """
        return lucro_html, margem_html, roi_html
    
    # Conectar eventos do botão de atualizar
    btn_atualizar.click(
        fn=atualizar_dashboard_receita,
        outputs=[
            grafico_pizza, grafico_barras_receita, grafico_acumulado_receita,
            ticket_medio_value, nps_value, receita_total_value
        ]
    ).then(
        fn=atualizar_boxes_receita,
        inputs=[ticket_medio_value, nps_value, receita_total_value],
        outputs=[ticket_medio_box, nps_box, receita_total_box]
    )
    
    btn_atualizar.click(
        fn=atualizar_dashboard_custos,
        outputs=[
            grafico_gastos_categoria, grafico_gastos_mensais, grafico_gastos_acumulados,
            gastos_total_value, gasto_medio_value
        ]
    ).then(
        fn=atualizar_boxes_custos,
        inputs=[gastos_total_value, gasto_medio_value],
        outputs=[gastos_total_box, gasto_medio_box]
    )
    
    btn_atualizar.click(
        fn=atualizar_dashboard_lucro,
        outputs=[
            grafico_lucro_mensal, grafico_receita_vs_gastos, grafico_lucro_acumulado,
            lucro_total_value, margem_lucro_value, roi_value
        ]
    ).then(
        fn=atualizar_boxes_lucro,
        inputs=[lucro_total_value, margem_lucro_value, roi_value],
        outputs=[lucro_total_box, margem_lucro_box, roi_box]
    )
    
    # Carregar dados iniciais
    dashboard.load(
        fn=atualizar_dashboard_receita,
        outputs=[
            grafico_pizza, grafico_barras_receita, grafico_acumulado_receita,
            ticket_medio_value, nps_value, receita_total_value
        ]
    ).then(
        fn=atualizar_boxes_receita,
        inputs=[ticket_medio_value, nps_value, receita_total_value],
        outputs=[ticket_medio_box, nps_box, receita_total_box]
    )
    
    dashboard.load(
        fn=atualizar_dashboard_custos,
        outputs=[
            grafico_gastos_categoria, grafico_gastos_mensais, grafico_gastos_acumulados,
            gastos_total_value, gasto_medio_value
        ]
    ).then(
        fn=atualizar_boxes_custos,
        inputs=[gastos_total_value, gasto_medio_value],
        outputs=[gastos_total_box, gasto_medio_box]
    )
    
    dashboard.load(
        fn=atualizar_dashboard_lucro,
        outputs=[
            grafico_lucro_mensal, grafico_receita_vs_gastos, grafico_lucro_acumulado,
            lucro_total_value, margem_lucro_value, roi_value
        ]
    ).then(
        fn=atualizar_boxes_lucro,
        inputs=[lucro_total_value, margem_lucro_value, roi_value],
        outputs=[lucro_total_box, margem_lucro_box, roi_box]
    )

if __name__ == "__main__":
    dashboard.launch(share=False, server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
