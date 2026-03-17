import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import urllib.parse
import os
from io import BytesIO

# ==================== CONFIGURAÇÕES DA EMPRESA ====================
EMPRESA = {
    "nome": "Oficina Mecânica Express",
    "nome_fantasia": "Express Auto Center",
    "cnpj": "12.345.678/0001-90",
    "ie": "123.456.789.000",
    "telefone": "(11) 3333-4444",
    "celular": "(11) 99999-9999",
    "email": "contato@expressauto.com.br",
    "site": "www.expressauto.com.br",
    "endereco": "Rua das Oficinas, 123 - Jardim das Autopeças",
    "cidade": "São Paulo - SP",
    "cep": "01234-567",
    "logo": "🚗",  # Emoji para representar logo (pode substituir por caminho de imagem)
    "slogan": "Qualidade e confiança em serviços automotivos",
    "redes_sociais": {
        "instagram": "@expressauto",
        "facebook": "/expressauto",
        "whatsapp": "5511999999999"
    }
}

# ==================== CONFIGURAÇÃO INICIAL ====================
st.set_page_config(
    page_title=f"{EMPRESA['nome_fantasia']} - Sistema", 
    layout="wide", 
    initial_sidebar_state="expanded",
    page_icon="🚗"
)

# ==================== ESTILO CSS PERSONALIZADO ====================
st.markdown(f"""
<style>
    .stButton > button {{
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }}
    .stDownloadButton > button {{
        background-color: #28a745;
        color: white;
        font-weight: bold;
    }}
    .success-box {{
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }}
    .warning-box {{
        padding: 20px;
        border-radius: 10px;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }}
    .metric-card {{
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 24px;
        font-weight: bold;
    }}
    div[data-testid="stMetricDelta"] {{
        font-size: 14px;
    }}
    .stDataFrame {{
        border: 1px solid #ddd;
        border-radius: 10px;
        overflow: hidden;
    }}
    h1, h2, h3 {{
        color: #2c3e50;
    }}
    .stSidebar .stRadio > label {{
        font-size: 16px;
        padding: 10px;
        border-radius: 5px;
    }}
    .stSidebar .stRadio > label:hover {{
        background-color: #f0f2f6;
    }}
    .empresa-header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }}
    .empresa-logo {{
        font-size: 48px;
        text-align: center;
    }}
    .empresa-nome {{
        font-size: 24px;
        font-weight: bold;
        text-align: center;
    }}
    .empresa-info {{
        font-size: 14px;
        text-align: center;
        opacity: 0.9;
    }}
    .login-header {{
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px 10px 0 0;
    }}
</style>
""", unsafe_allow_html=True)

# ==================== FUNÇÕES AUXILIARES ====================
def format_currency(value):
    """Formata valor para moeda brasileira"""
    if pd.isna(value) or value is None:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def convert_to_bytes(pdf_output):
    """Converte diferentes tipos de retorno do FPDF para bytes"""
    if isinstance(pdf_output, str):
        return pdf_output.encode('latin1')
    elif isinstance(pdf_output, bytearray):
        return bytes(pdf_output)
    else:
        return pdf_output  # Já deve ser bytes

def show_empresa_header():
    """Mostra cabeçalho da empresa na dashboard"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="empresa-header">
            <div class="empresa-logo">{EMPRESA['logo']}</div>
            <div class="empresa-nome">{EMPRESA['nome']}</div>
            <div class="empresa-info">{EMPRESA['slogan']}</div>
            <div class="empresa-info">{EMPRESA['endereco']} - {EMPRESA['cidade']}</div>
            <div class="empresa-info">📞 {EMPRESA['telefone']} | 📱 {EMPRESA['celular']}</div>
            <div class="empresa-info">✉️ {EMPRESA['email']} | 🌐 {EMPRESA['site']}</div>
        </div>
        """, unsafe_allow_html=True)

# ==================== LOGIN ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

USUARIOS = {
    "admin": "1234",
    "mecanico": "oficina2025",
    "gerente": "gerente123"
}

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Cabeçalho da empresa na tela de login
        st.markdown(f"""
        <div class="login-header">
            <div style="font-size: 64px;">{EMPRESA['logo']}</div>
            <div style="font-size: 28px; font-weight: bold;">{EMPRESA['nome']}</div>
            <div style="font-size: 16px;">{EMPRESA['slogan']}</div>
            <div style="font-size: 14px; margin-top: 10px;">{EMPRESA['endereco']}</div>
            <div style="font-size: 14px;">{EMPRESA['telefone']} | {EMPRESA['email']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("## 🔐 Acesso ao Sistema")
        
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("🔑 Senha", type="password", placeholder="Digite sua senha")
            submit = st.form_submit_button("🚪 Entrar", use_container_width=True)
            
            if submit:
                if usuario in USUARIOS and USUARIOS[usuario] == senha:
                    st.session_state.logged_in = True
                    st.session_state.username = usuario
                    st.success(f"✅ Bem-vindo, {usuario}!")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos")
        
        with st.expander("ℹ️ Credenciais de teste"):
            st.markdown("""
            - **admin** / 1234
            - **mecanico** / oficina2025
            - **gerente** / gerente123
            """)
        
        # Rodapé da empresa no login
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center; color: gray; font-size: 12px;">
            {EMPRESA['nome']} - {EMPRESA['cnpj']}<br>
            {EMPRESA['endereco']} - {EMPRESA['cidade']} - CEP: {EMPRESA['cep']}<br>
            © {datetime.now().year} - Todos os direitos reservados
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ==================== BANCO DE DADOS ====================
@st.cache_resource
def init_database():
    """Inicializa o banco de dados e cria tabelas se não existirem"""
    conn = sqlite3.connect('oficina.db', check_same_thread=False)
    c = conn.cursor()
    
    # Criar tabelas
    c.execute('''CREATE TABLE IF NOT EXISTS clientes 
                 (id INTEGER PRIMARY KEY, nome TEXT, telefone TEXT, cpf TEXT, email TEXT, endereco TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS veiculos 
                 (id INTEGER PRIMARY KEY, cliente_id INTEGER, placa TEXT, modelo TEXT, 
                  ano INTEGER, cor TEXT, foto BLOB, observacoes TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS os 
                 (id INTEGER PRIMARY KEY, data TEXT, cliente_id INTEGER, veiculo_id INTEGER, 
                  total REAL, status TEXT, forma_pagamento TEXT, observacoes TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS os_itens 
                 (id INTEGER PRIMARY KEY, os_id INTEGER, descricao TEXT, 
                  quantidade REAL, preco REAL, tipo TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS despesas 
                 (id INTEGER PRIMARY KEY, data TEXT, descricao TEXT, valor REAL, categoria TEXT)''')
    
    # Adicionar colunas se não existirem (para compatibilidade)
    try:
        c.execute("ALTER TABLE veiculos ADD COLUMN foto BLOB")
    except:
        pass
    try:
        c.execute("ALTER TABLE veiculos ADD COLUMN ano INTEGER")
    except:
        pass
    try:
        c.execute("ALTER TABLE veiculos ADD COLUMN cor TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE veiculos ADD COLUMN observacoes TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE clientes ADD COLUMN email TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE clientes ADD COLUMN endereco TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE os ADD COLUMN forma_pagamento TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE os ADD COLUMN observacoes TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE os_itens ADD COLUMN tipo TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE despesas ADD COLUMN categoria TEXT")
    except:
        pass
    
    conn.commit()
    return conn, c

conn, c = init_database()

# ==================== FUNÇÕES DE CONSULTA ====================
def get_clientes():
    """Retorna lista de clientes"""
    c.execute("SELECT id, nome, telefone FROM clientes ORDER BY nome")
    return c.fetchall()

def get_veiculos(cliente_id=None):
    """Retorna lista de veículos de um cliente específico ou todos"""
    if cliente_id:
        c.execute("SELECT id, placa, modelo FROM veiculos WHERE cliente_id=? ORDER BY placa", (cliente_id,))
    else:
        c.execute("SELECT id, placa, modelo FROM veiculos ORDER BY placa")
    return c.fetchall()

def get_os_abertas():
    """Retorna número de OS abertas"""
    c.execute("SELECT COUNT(*) FROM os WHERE status='Aberta'")
    return c.fetchone()[0]

def get_total_mes():
    """Retorna total faturado no mês atual"""
    c.execute("""
        SELECT SUM(total) FROM os 
        WHERE status='Concluída' 
        AND strftime('%m', substr(data,7,4)||'-'||substr(data,4,2)||'-'||substr(data,1,2)) = strftime('%m', 'now')
    """)
    return c.fetchone()[0] or 0

# ==================== SIDEBAR ====================
with st.sidebar:
    # Informações da empresa na sidebar
    st.markdown(f"""
    <div style="text-align: center; padding: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
        <div style="font-size: 32px;">{EMPRESA['logo']}</div>
        <div style="font-size: 16px; font-weight: bold;">{EMPRESA['nome_fantasia']}</div>
        <div style="font-size: 10px;">{EMPRESA['cnpj']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### 👋 Olá, **{st.session_state.username}**!")
    st.markdown("---")
    
    # Menu principal
    menu = st.radio(
        "📋 Navegação",
        ["🏠 Dashboard",
         "👤 Cadastrar Cliente",
         "🚘 Cadastrar Veículo",
         "📋 Nova Ordem de Serviço",
         "📋 Listar Ordens de Serviço",
         "👥 Gerenciar Clientes",
         "💰 Relatório de Gastos e Lucro",
         "📄 Gerar NF-e (PDF)"]
    )
    
    st.markdown("---")
    
    # Estatísticas rápidas
    st.markdown("### 📊 Estatísticas Rápidas")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("OS Abertas", get_os_abertas())
    with col2:
        st.metric("Faturamento Mês", format_currency(get_total_mes()))
    
    st.markdown("---")
    
    # Informações de contato na sidebar
    with st.expander("📞 Contato da Empresa"):
        st.markdown(f"""
        **Telefone:** {EMPRESA['telefone']}  
        **WhatsApp:** {EMPRESA['celular']}  
        **Email:** {EMPRESA['email']}  
        **Site:** {EMPRESA['site']}  
        **Instagram:** {EMPRESA['redes_sociais']['instagram']}  
        **Facebook:** {EMPRESA['redes_sociais']['facebook']}
        """)
    
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ==================== DASHBOARD ====================
if menu == "🏠 Dashboard":
    st.title(f"🏠 {EMPRESA['nome_fantasia']} - Dashboard")
    
    # Mostrar cabeçalho da empresa
    show_empresa_header()
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        c.execute("SELECT COUNT(*) FROM clientes")
        total_clientes = c.fetchone()[0]
        st.metric("👥 Total Clientes", total_clientes)
    
    with col2:
        c.execute("SELECT COUNT(*) FROM veiculos")
        total_veiculos = c.fetchone()[0]
        st.metric("🚗 Total Veículos", total_veiculos)
    
    with col3:
        c.execute("SELECT COUNT(*) FROM os WHERE status='Aberta'")
        os_abertas = c.fetchone()[0]
        st.metric("📋 OS em Aberto", os_abertas)
    
    with col4:
        c.execute("SELECT COUNT(*) FROM os WHERE status='Concluída'")
        os_concluidas = c.fetchone()[0]
        st.metric("✅ OS Concluídas", os_concluidas)
    
    st.markdown("---")
    
    # Gráficos e análises
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Últimas OS")
        df_ultimas = pd.read_sql_query("""
            SELECT os.id, os.data, clientes.nome, os.total, os.status 
            FROM os 
            JOIN clientes ON os.cliente_id = clientes.id 
            ORDER BY os.id DESC LIMIT 5
        """, conn)
        
        if not df_ultimas.empty:
            df_ultimas['total'] = df_ultimas['total'].apply(format_currency)
            st.dataframe(df_ultimas, use_container_width=True)
        else:
            st.info("Nenhuma OS cadastrada ainda")
    
    with col2:
        st.subheader("💰 Receita vs Despesas (Mês)")
        
        # Receita do mês
        c.execute("""
            SELECT SUM(total) FROM os 
            WHERE status='Concluída' 
            AND strftime('%m', substr(data,7,4)||'-'||substr(data,4,2)||'-'||substr(data,1,2)) = strftime('%m', 'now')
        """)
        receita_mes = c.fetchone()[0] or 0
        
        # Despesa do mês
        c.execute("""
            SELECT SUM(valor) FROM despesas 
            WHERE strftime('%m', substr(data,7,4)||'-'||substr(data,4,2)||'-'||substr(data,1,2)) = strftime('%m', 'now')
        """)
        despesa_mes = c.fetchone()[0] or 0
        
        lucro_mes = receita_mes - despesa_mes
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Receita", format_currency(receita_mes))
        col_b.metric("Despesa", format_currency(despesa_mes))
        col_c.metric("Lucro", format_currency(lucro_mes), 
                    delta=f"{((lucro_mes/receita_mes)*100 if receita_mes > 0 else 0):.1f}%")

# ==================== CADASTRAR CLIENTE ====================
elif menu == "👤 Cadastrar Cliente":
    st.title("👤 Cadastrar Novo Cliente")
    
    with st.form("form_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("📝 Nome completo *", placeholder="Digite o nome completo")
            telefone = st.text_input("📱 Telefone *", placeholder="(11) 99999-9999")
            cpf = st.text_input("🆔 CPF", placeholder="000.000.000-00")
        
        with col2:
            email = st.text_input("📧 E-mail", placeholder="cliente@email.com")
            endereco = st.text_input("📍 Endereço", placeholder="Rua, número, bairro")
        
        st.markdown("---")
        submitted = st.form_submit_button("💾 Salvar Cliente", use_container_width=True)
        
        if submitted:
            if nome and telefone:
                try:
                    c.execute("""
                        INSERT INTO clientes (nome, telefone, cpf, email, endereco) 
                        VALUES (?,?,?,?,?)
                    """, (nome, telefone, cpf, email, endereco))
                    conn.commit()
                    st.success("✅ Cliente cadastrado com sucesso!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro ao cadastrar: {str(e)}")
            else:
                st.error("❌ Nome e telefone são obrigatórios!")

# ==================== CADASTRAR VEÍCULO ====================
elif menu == "🚘 Cadastrar Veículo":
    st.title("🚘 Cadastrar Veículo")
    
    clientes = get_clientes()
    
    if not clientes:
        st.warning("⚠️ Cadastre um cliente primeiro!")
    else:
        with st.form("form_veiculo", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                cliente_dict = {f"{id} - {nome}": id for id, nome, _ in clientes}
                cliente_selecionado = st.selectbox("👤 Cliente *", list(cliente_dict.keys()))
                placa = st.text_input("🔢 Placa *", placeholder="ABC-1234").upper()
                modelo = st.text_input("🚗 Modelo *", placeholder="Fusca 1978")
            
            with col2:
                ano = st.number_input("📅 Ano", min_value=1900, max_value=datetime.now().year + 1, value=2000)
                cor = st.text_input("🎨 Cor", placeholder="Azul")
                foto = st.file_uploader("📸 Foto do veículo", type=["jpg", "jpeg", "png"])
            
            observacoes = st.text_area("📝 Observações", placeholder="Informações adicionais sobre o veículo")
            
            st.markdown("---")
            submitted = st.form_submit_button("💾 Salvar Veículo", use_container_width=True)
            
            if submitted:
                if placa and modelo:
                    try:
                        cliente_id = cliente_dict[cliente_selecionado]
                        foto_bytes = foto.read() if foto else None
                        
                        c.execute("""
                            INSERT INTO veiculos (cliente_id, placa, modelo, ano, cor, foto, observacoes) 
                            VALUES (?,?,?,?,?,?,?)
                        """, (cliente_id, placa, modelo, ano, cor, foto_bytes, observacoes))
                        
                        conn.commit()
                        st.success("✅ Veículo cadastrado com sucesso!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Erro ao cadastrar: {str(e)}")
                else:
                    st.error("❌ Placa e modelo são obrigatórios!")

# ==================== NOVA ORDEM DE SERVIÇO ====================
elif menu == "📋 Nova Ordem de Serviço":
    st.title("📋 Nova Ordem de Serviço")
    
    # Inicializar sessão para itens
    if "itens_os" not in st.session_state:
        st.session_state.itens_os = []
    
    # Seleção de cliente e veículo
    col1, col2 = st.columns(2)
    
    with col1:
        clientes = get_clientes()
        if clientes:
            cliente_dict = {f"{id} - {nome}": id for id, nome, _ in clientes}
            cliente_selecionado = st.selectbox("👤 Selecione o Cliente", list(cliente_dict.keys()))
            cliente_id = cliente_dict[cliente_selecionado]
        else:
            st.warning("Cadastre um cliente primeiro!")
            st.stop()
    
    with col2:
        veiculos = get_veiculos(cliente_id)
        if veiculos:
            veiculo_dict = {f"{id} - {placa} - {modelo}": id for id, placa, modelo in veiculos}
            veiculo_selecionado = st.selectbox("🚘 Selecione o Veículo", list(veiculo_dict.keys()))
            veiculo_id = veiculo_dict[veiculo_selecionado]
            
            # Mostrar foto do veículo
            c.execute("SELECT foto FROM veiculos WHERE id=?", (veiculo_id,))
            foto_data = c.fetchone()
            if foto_data and foto_data[0]:
                st.image(foto_data[0], caption="📸 Foto do veículo", width=300)
        else:
            st.warning("Cadastre um veículo para este cliente primeiro!")
            st.stop()
    
    st.markdown("---")
    
    # Itens da OS
    st.subheader("🛠️ Itens da Ordem de Serviço")
    
    # Formulário para adicionar itens
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        descricao = st.text_input("Descrição do item", key="desc_item")
    with col2:
        tipo = st.selectbox("Tipo", ["Serviço", "Peça"], key="tipo_item")
    with col3:
        quantidade = st.number_input("Quantidade", min_value=0.1, step=0.1, key="qtd_item")
    with col4:
        preco = st.number_input("Preço unitário R$", min_value=0.0, step=0.1, key="preco_item")
    
    if st.button("➕ Adicionar Item", use_container_width=True):
        if descricao and quantidade > 0 and preco > 0:
            subtotal = quantidade * preco
            st.session_state.itens_os.append({
                "descricao": descricao,
                "tipo": tipo,
                "quantidade": quantidade,
                "preco": preco,
                "subtotal": subtotal
            })
            st.rerun()
        else:
            st.error("Preencha todos os campos corretamente!")
    
    # Lista de itens adicionados
    if st.session_state.itens_os:
        df_itens = pd.DataFrame(st.session_state.itens_os)
        st.dataframe(df_itens, use_container_width=True)
        
        total_os = df_itens["subtotal"].sum()
        st.success(f"### 💰 TOTAL DA OS: {format_currency(total_os)}")
        
        # Observações e forma de pagamento
        col1, col2 = st.columns(2)
        with col1:
            observacoes = st.text_area("📝 Observações da OS")
        with col2:
            forma_pagamento = st.selectbox("💰 Forma de Pagamento", 
                                         ["Dinheiro", "Cartão Débito", "Cartão Crédito", "PIX", "Boleto", "Fiado"])
        
        # Botão para salvar
        if st.button("💾 Salvar Ordem de Serviço", type="primary", use_container_width=True):
            try:
                c.execute("""
                    INSERT INTO os (data, cliente_id, veiculo_id, total, status, forma_pagamento, observacoes) 
                    VALUES (?,?,?,?,?,?,?)
                """, (datetime.now().strftime("%d/%m/%Y"), cliente_id, veiculo_id, 
                      total_os, "Aberta", forma_pagamento, observacoes))
                
                os_id = c.lastrowid
                
                for item in st.session_state.itens_os:
                    c.execute("""
                        INSERT INTO os_itens (os_id, descricao, quantidade, preco, tipo) 
                        VALUES (?,?,?,?,?)
                    """, (os_id, item["descricao"], item["quantidade"], item["preco"], item["tipo"]))
                
                conn.commit()
                st.success(f"✅ Ordem de Serviço #{os_id} salva com sucesso!")
                st.balloons()
                st.session_state.itens_os = []
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {str(e)}")
    else:
        st.info("Adicione itens à ordem de serviço")

# ==================== LISTAR ORDENS DE SERVIÇO ====================
elif menu == "📋 Listar Ordens de Serviço":
    st.title("📋 Ordens de Serviço")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filtrar por Status", ["Todas", "Aberta", "Concluída", "Cancelada"])
    with col2:
        data_filter = st.date_input("Filtrar por Data", value=None)
    with col3:
        search = st.text_input("🔍 Buscar por cliente ou placa")
    
    # Query base
    query = """
        SELECT os.id, os.data, clientes.nome as cliente, 
               veiculos.placa, veiculos.modelo, os.total, os.status 
        FROM os 
        JOIN clientes ON os.cliente_id = clientes.id 
        JOIN veiculos ON os.veiculo_id = veiculos.id 
        WHERE 1=1
    """
    params = []
    
    if status_filter != "Todas":
        query += " AND os.status = ?"
        params.append(status_filter)
    
    if data_filter:
        query += " AND os.data = ?"
        params.append(data_filter.strftime("%d/%m/%Y"))
    
    if search:
        query += " AND (clientes.nome LIKE ? OR veiculos.placa LIKE ?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")
    
    query += " ORDER BY os.id DESC"
    
    df_os = pd.read_sql_query(query, conn, params=params)
    
    if not df_os.empty:
        # Formatar valores
        df_os['total'] = df_os['total'].apply(format_currency)
        st.dataframe(df_os, use_container_width=True)
        
        # Ações para cada OS
        st.subheader("🔄 Ações")
        os_id = st.selectbox("Selecione a OS para ações", df_os['id'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Concluir OS", use_container_width=True):
                c.execute("UPDATE os SET status='Concluída' WHERE id=?", (os_id,))
                conn.commit()
                st.success("OS concluída!")
                st.rerun()
        with col2:
            if st.button("❌ Cancelar OS", use_container_width=True):
                c.execute("UPDATE os SET status='Cancelada' WHERE id=?", (os_id,))
                conn.commit()
                st.success("OS cancelada!")
                st.rerun()
        with col3:
            if st.button("📄 Ver Detalhes", use_container_width=True):
                st.session_state['ver_os'] = os_id
                st.rerun()
        
        # Mostrar detalhes se selecionado
        if 'ver_os' in st.session_state and st.session_state['ver_os'] == os_id:
            st.markdown("---")
            st.subheader(f"📄 Detalhes da OS #{os_id}")
            
            # Dados da OS
            os_data = pd.read_sql_query(f"SELECT * FROM os WHERE id={os_id}", conn).iloc[0]
            itens = pd.read_sql_query(f"SELECT * FROM os_itens WHERE os_id={os_id}", conn)
            
            st.write(f"**Data:** {os_data['data']}")
            st.write(f"**Status:** {os_data['status']}")
            st.write(f"**Forma de Pagamento:** {os_data['forma_pagamento']}")
            st.write(f"**Total:** {format_currency(os_data['total'])}")
            
            if pd.notna(os_data['observacoes']):
                st.write(f"**Observações:** {os_data['observacoes']}")
            
            st.dataframe(itens, use_container_width=True)
            
            if st.button("Fechar Detalhes"):
                del st.session_state['ver_os']
                st.rerun()
    else:
        st.info("Nenhuma OS encontrada com os filtros selecionados")

# ==================== GERENCIAR CLIENTES ====================
elif menu == "👥 Gerenciar Clientes":
    st.title("👥 Gerenciar Clientes")
    
    # Lista de clientes
    df_clientes = pd.read_sql_query("SELECT * FROM clientes ORDER BY nome", conn)
    
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True)
        
        st.markdown("---")
        st.subheader("✏️ Editar / Excluir Cliente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✏️ Editar Cliente")
            cliente_id = st.number_input("ID do cliente para editar", min_value=1, step=1)
            
            if st.button("Carregar Dados", use_container_width=True):
                c.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,))
                dados = c.fetchone()
                if dados:
                    with st.form("edit_form"):
                        novo_nome = st.text_input("Nome", value=dados[1])
                        novo_telefone = st.text_input("Telefone", value=dados[2])
                        novo_cpf = st.text_input("CPF", value=dados[3] if len(dados) > 3 else "")
                        novo_email = st.text_input("Email", value=dados[4] if len(dados) > 4 else "")
                        novo_endereco = st.text_input("Endereço", value=dados[5] if len(dados) > 5 else "")
                        
                        if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                            try:
                                c.execute("""
                                    UPDATE clientes 
                                    SET nome=?, telefone=?, cpf=?, email=?, endereco=? 
                                    WHERE id=?
                                """, (novo_nome, novo_telefone, novo_cpf, novo_email, novo_endereco, cliente_id))
                                conn.commit()
                                st.success("✅ Cliente atualizado!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar: {str(e)}")
                else:
                    st.error("Cliente não encontrado")
        
        with col2:
            st.markdown("### 🗑️ Excluir Cliente")
            st.warning("⚠️ Cuidado: Esta ação não pode ser desfeita!")
            cliente_id_del = st.number_input("ID do cliente para excluir", min_value=1, step=1, key="del_id")
            
            if st.button("Excluir Cliente", type="primary", use_container_width=True):
                # Verificar se cliente tem veículos ou OS
                c.execute("SELECT COUNT(*) FROM veiculos WHERE cliente_id=?", (cliente_id_del,))
                tem_veiculos = c.fetchone()[0] > 0
                
                c.execute("SELECT COUNT(*) FROM os WHERE cliente_id=?", (cliente_id_del,))
                tem_os = c.fetchone()[0] > 0
                
                if tem_veiculos or tem_os:
                    st.error("Não é possível excluir cliente com veículos ou OS vinculadas!")
                else:
                    try:
                        c.execute("DELETE FROM clientes WHERE id=?", (cliente_id_del,))
                        conn.commit()
                        st.success("✅ Cliente excluído!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {str(e)}")
    else:
        st.info("Nenhum cliente cadastrado")

# ==================== RELATÓRIO DE GASTOS E LUCRO ====================
elif menu == "💰 Relatório de Gastos e Lucro":
    st.title("💰 Relatório Financeiro")
    
    # Filtro de período
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Início", value=datetime.now().replace(day=1))
    with col2:
        data_fim = st.date_input("Data Fim", value=datetime.now())
    
    # Converter datas para comparação no formato YYYYMMDD
    inicio_comp = data_inicio.strftime("%Y%m%d")
    fim_comp = data_fim.strftime("%Y%m%d")
    
    # Consultas com filtro de data
    df_os_periodo = pd.read_sql_query("""
        SELECT * FROM os 
        WHERE status='Concluída'
        AND substr(data,7,4)||substr(data,4,2)||substr(data,1,2) BETWEEN ? AND ?
        ORDER BY data
    """, conn, params=[inicio_comp, fim_comp])
    
    df_despesas_periodo = pd.read_sql_query("""
        SELECT * FROM despesas 
        WHERE substr(data,7,4)||substr(data,4,2)||substr(data,1,2) BETWEEN ? AND ?
        ORDER BY data
    """, conn, params=[inicio_comp, fim_comp])
    
    total_os = df_os_periodo['total'].sum() if not df_os_periodo.empty else 0
    total_despesas = df_despesas_periodo['valor'].sum() if not df_despesas_periodo.empty else 0
    lucro = total_os - total_despesas
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📈 Total Recebido (OS)", format_currency(total_os))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📉 Total Despesas", format_currency(total_despesas))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        delta_color = "normal" if lucro >= 0 else "inverse"
        st.metric("💵 LUCRO", format_currency(lucro), 
                 delta=f"{((lucro/total_os)*100 if total_os > 0 else 0):.1f}%", 
                 delta_color=delta_color)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Listagem de OS do período
    st.subheader("📋 Ordens de Serviço Concluídas no Período")
    if not df_os_periodo.empty:
        df_os_periodo['total'] = df_os_periodo['total'].apply(format_currency)
        st.dataframe(df_os_periodo[['id', 'data', 'total', 'forma_pagamento']], use_container_width=True)
    else:
        st.info("Nenhuma OS concluída no período")
    
    # Listagem de despesas do período
    st.subheader("📋 Despesas do Período")
    if not df_despesas_periodo.empty:
        df_despesas_periodo['valor'] = df_despesas_periodo['valor'].apply(format_currency)
        st.dataframe(df_despesas_periodo[['data', 'descricao', 'categoria', 'valor']], use_container_width=True)
    else:
        st.info("Nenhuma despesa no período")
    
    st.markdown("---")
    st.subheader("➕ Adicionar Nova Despesa")
    
    with st.form("nova_despesa", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            desc_despesa = st.text_input("Descrição da despesa *")
        with col2:
            valor_despesa = st.number_input("Valor R$ *", min_value=0.01, step=0.01)
        with col3:
            categoria = st.selectbox("Categoria", ["Material", "Mão de obra", "Aluguel", "Água/Luz", "Impostos", "Outros"])
        
        if st.form_submit_button("💾 Registrar Despesa", use_container_width=True):
            if desc_despesa and valor_despesa > 0:
                try:
                    c.execute("""
                        INSERT INTO despesas (data, descricao, valor, categoria) 
                        VALUES (?,?,?,?)
                    """, (datetime.now().strftime("%d/%m/%Y"), desc_despesa, valor_despesa, categoria))
                    conn.commit()
                    st.success("✅ Despesa registrada!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao registrar: {str(e)}")
            else:
                st.error("Preencha todos os campos!")

# ==================== GERAR NF-e PDF ====================
elif menu == "📄 Gerar NF-e (PDF)":
    st.title("📄 Gerar NF-e em PDF")
    
    # Buscar OS disponíveis
    df_os = pd.read_sql_query("""
        SELECT os.id, os.data, clientes.nome as cliente, os.total 
        FROM os 
        JOIN clientes ON os.cliente_id = clientes.id 
        WHERE os.status != 'Cancelada'
        ORDER BY os.id DESC
    """, conn)
    
    if not df_os.empty:
        # Formatar valores para exibição
        df_os_display = df_os.copy()
        df_os_display['total'] = df_os_display['total'].apply(format_currency)
        
        st.dataframe(df_os_display, use_container_width=True)
        
        os_id = st.selectbox("🔍 Selecione a OS para gerar PDF", df_os['id'])
        
        if st.button("📄 Gerar PDF", type="primary", use_container_width=True):
            try:
                # Buscar dados completos da OS
                os_data = pd.read_sql_query(f"SELECT * FROM os WHERE id={os_id}", conn).iloc[0]
                itens = pd.read_sql_query(f"SELECT * FROM os_itens WHERE os_id={os_id}", conn)
                cliente = pd.read_sql_query(f"SELECT * FROM clientes WHERE id={os_data['cliente_id']}", conn).iloc[0]
                veiculo = pd.read_sql_query(f"SELECT * FROM veiculos WHERE id={os_data['veiculo_id']}", conn).iloc[0]
                
                # Criar PDF
                pdf = FPDF()
                pdf.add_page()
                
                # ===== CABEÇALHO DA EMPRESA NO PDF =====
                pdf.set_fill_color(52, 73, 94)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Arial", "B", 20)
                pdf.cell(0, 15, EMPRESA['nome'].upper(), 0, 1, "C", 1)
                
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, EMPRESA['slogan'], 0, 1, "C", 1)
                pdf.ln(5)
                
                # Informações da empresa
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 6, f"CNPJ: {EMPRESA['cnpj']} | IE: {EMPRESA['ie']}", 0, 1, "C")
                pdf.cell(0, 6, f"{EMPRESA['endereco']} - {EMPRESA['cidade']} - CEP: {EMPRESA['cep']}", 0, 1, "C")
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, f"Tel: {EMPRESA['telefone']} | Cel: {EMPRESA['celular']} | Email: {EMPRESA['email']}", 0, 1, "C")
                pdf.ln(10)
                
                # Linha divisória
                pdf.set_draw_color(52, 73, 94)
                pdf.set_line_width(0.5)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(10)
                
                # Informações da OS
                pdf.set_fill_color(240, 240, 240)
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, f"NOTA FISCAL DE SERVIÇOS - OS Nº {os_id}", 0, 1, "C", 1)
                pdf.ln(5)
                
                # Dados da OS
                pdf.set_font("Arial", "B", 10)
                pdf.cell(30, 8, "Data:", 0, 0)
                pdf.set_font("Arial", "", 10)
                pdf.cell(60, 8, os_data['data'], 0, 0)
                
                pdf.set_font("Arial", "B", 10)
                pdf.cell(30, 8, "Status:", 0, 0)
                pdf.set_font("Arial", "", 10)
                status_color = (46, 204, 113) if os_data['status'] == 'Concluída' else (241, 196, 15)
                pdf.set_text_color(*status_color)
                pdf.cell(60, 8, os_data['status'], 0, 1)
                
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Arial", "B", 10)
                pdf.cell(30, 8, "Pagamento:", 0, 0)
                pdf.set_font("Arial", "", 10)
                pdf.cell(60, 8, os_data['forma_pagamento'] if pd.notna(os_data['forma_pagamento']) else "Não informado", 0, 1)
                pdf.ln(5)
                
                # Dados do cliente
                pdf.set_fill_color(240, 240, 240)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, "DADOS DO CLIENTE", 0, 1, "L", 1)
                pdf.ln(5)
                
                pdf.set_font("Arial", "B", 10)
                pdf.cell(20, 6, "Nome:", 0, 0)
                pdf.set_font("Arial", "", 10)
                pdf.cell(80, 6, cliente['nome'], 0, 0)
                
                pdf.set_font("Arial", "B", 10)
                pdf.cell(25, 6, "Telefone:", 0, 0)
                pdf.set_font("Arial", "", 10)
                pdf.cell(60, 6, cliente['telefone'], 0, 1)
                
                if pd.notna(cliente['cpf']):
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(20, 6, "CPF:", 0, 0)
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(80, 6, cliente['cpf'], 0, 0)
                
                if pd.notna(cliente['email']):
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(25, 6, "E-mail:", 0, 0)
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(60, 6, cliente['email'], 0, 1)
                
                if pd.notna(cliente['endereco']):
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(20, 6, "End.:", 0, 0)
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(0, 6, cliente['endereco'], 0, 1)
                pdf.ln(10)
                
                # Dados do veículo
                pdf.set_fill_color(240, 240, 240)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, "DADOS DO VEÍCULO", 0, 1, "L", 1)
                pdf.ln(5)
                
                pdf.set_font("Arial", "B", 10)
                pdf.cell(25, 6, "Placa:", 0, 0)
                pdf.set_font("Arial", "", 10)
                pdf.cell(60, 6, veiculo['placa'], 0, 0)
                
                pdf.set_font("Arial", "B", 10)
                pdf.cell(30, 6, "Modelo:", 0, 0)
                pdf.set_font("Arial", "", 10)
                pdf.cell(70, 6, veiculo['modelo'], 0, 1)
                
                if pd.notna(veiculo['ano']):
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(25, 6, "Ano:", 0, 0)
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(60, 6, str(veiculo['ano']), 0, 0)
                
                if pd.notna(veiculo['cor']):
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(30, 6, "Cor:", 0, 0)
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(70, 6, veiculo['cor'], 0, 1)
                pdf.ln(10)
                
                # Tabela de itens
                pdf.set_fill_color(52, 73, 94)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Arial", "B", 10)
                
                # Cabeçalho da tabela
                pdf.cell(80, 10, "Descrição", 1, 0, "C", 1)
                pdf.cell(20, 10, "Tipo", 1, 0, "C", 1)
                pdf.cell(25, 10, "Quantidade", 1, 0, "C", 1)
                pdf.cell(30, 10, "Preço Unit.", 1, 0, "C", 1)
                pdf.cell(30, 10, "Subtotal", 1, 1, "C", 1)
                
                # Itens
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Arial", "", 9)
                total = 0
                
                for _, item in itens.iterrows():
                    subtotal = item['quantidade'] * item['preco']
                    total += subtotal
                    
                    # Descrição (limitada a 40 caracteres)
                    desc = item['descricao'][:40] + "..." if len(item['descricao']) > 40 else item['descricao']
                    pdf.cell(80, 8, desc, 1)
                    pdf.cell(20, 8, item['tipo'] if pd.notna(item['tipo']) else "Serviço", 1, 0, "C")
                    pdf.cell(25, 8, f"{item['quantidade']:.2f}", 1, 0, "C")
                    pdf.cell(30, 8, format_currency(item['preco']), 1, 0, "R")
                    pdf.cell(30, 8, format_currency(subtotal), 1, 1, "R")
                
                # Linha de total
                pdf.set_font("Arial", "B", 11)
                pdf.cell(155, 10, "TOTAL GERAL:", 1, 0, "R")
                pdf.set_fill_color(46, 204, 113)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(30, 10, format_currency(total), 1, 1, "R", 1)
                
                pdf.set_text_color(0, 0, 0)
                pdf.ln(10)
                
                # Observações
                if pd.notna(os_data['observacoes']):
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(0, 6, "Observações:", 0, 1)
                    pdf.set_font("Arial", "", 9)
                    pdf.multi_cell(0, 5, os_data['observacoes'])
                    pdf.ln(5)
                
                # ===== RODAPÉ DA EMPRESA NO PDF =====
                pdf.set_y(-45)
                pdf.set_draw_color(52, 73, 94)
                pdf.set_line_width(0.5)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(5)
                
                pdf.set_font("Arial", "B", 9)
                pdf.cell(0, 5, EMPRESA['nome'].upper(), 0, 1, "C")
                pdf.set_font("Arial", "", 8)
                pdf.cell(0, 4, EMPRESA['endereco'], 0, 1, "C")
                pdf.cell(0, 4, f"Tel: {EMPRESA['telefone']} | WhatsApp: {EMPRESA['celular']} | {EMPRESA['email']}", 0, 1, "C")
                pdf.cell(0, 4, f"{EMPRESA['site']} | {EMPRESA['redes_sociais']['instagram']}", 0, 1, "C")
                pdf.ln(2)
                pdf.cell(0, 4, f"Documento gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, "C")
                
                # 🔥 CORREÇÃO - Converter para bytes corretamente
                pdf_output = pdf.output(dest='S')
                pdf_bytes = convert_to_bytes(pdf_output)
                
                # Botão de download
                st.download_button(
                    label="📥 Baixar PDF",
                    data=pdf_bytes,
                    file_name=f"NF-e_{EMPRESA['nome_fantasia'].replace(' ', '_')}_OS_{os_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                # WhatsApp
                st.markdown("---")
                st.subheader("📱 Enviar por WhatsApp")
                
                # Limpar telefone
                telefone = str(cliente['telefone']).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
                if telefone:
                    if not telefone.startswith("55"):
                        telefone = "55" + telefone
                    
                    mensagem = f"Olá! Segue a NF-e da OS #{os_id} no valor de {format_currency(total)}. {EMPRESA['nome']} - {EMPRESA['telefone']}"
                    
                    link_whatsapp = f"https://wa.me/{telefone}?text={urllib.parse.quote(mensagem)}"
                    
                    st.link_button("📱 Abrir WhatsApp", link_whatsapp, use_container_width=True)
                    st.info("💡 Baixe o PDF e anexe à conversa do WhatsApp")
                
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {str(e)}")
                st.exception(e)
    else:
        st.info("Nenhuma OS disponível para gerar PDF")

# ==================== RODAPÉ ====================
st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
    <div style='text-align: center; color: gray; font-size: 11px;'>
        {EMPRESA['nome']}<br>
        {EMPRESA['cnpj']}<br>
        © {datetime.now().year} - v2.0
    </div>
    """, 
    unsafe_allow_html=True
)