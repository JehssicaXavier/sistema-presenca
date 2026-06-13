from flask import Flask, request, send_file
import sqlite3
from datetime import datetime, timedelta
import os
from openpyxl import Workbook

app = Flask(__name__)

def criar_banco():
    conn = sqlite3.connect("presenca.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alunos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS presencas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aluno TEXT NOT NULL,
        data TEXT NOT NULL,
        hora TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

criar_banco()

@app.route("/")
def inicio():
    return """
    <html><head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body{font-family:Arial;background:#f2f2f2;padding:20px;text-align:center}
    .topo{background:#0066cc;color:white;padding:20px;border-radius:12px}
    .botao{display:block;background:white;color:#333;text-decoration:none;padding:18px;margin:12px auto;width:85%;
    border:1px solid #ccc;border-radius:10px;font-size:18px;font-weight:bold}
    </style></head><body>
    <div class="topo">
    <h1>📚 Sistema Inteligente de Presença</h1>
    <p>Projeto Extensionista UNINTER</p>
    </div>

    <a class="botao" href="/cadastro">➕ Cadastrar Aluno</a>
    <a class="botao" href="/alunos">📋 Ver Alunos</a>
    <a class="botao" href="/chamada">🎤 Fazer Chamada</a>
    <a class="botao" href="/presencas">✅ Ver Presenças</a>
    <a class="botao" href="/dashboard">📊 Dashboard</a>
    <a class="botao" href="/relatorio">📑 Relatórios</a>
    <a class="botao" href="/excel">📊 Exportar Excel</a>
    </body></html>
    """

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]

        conn = sqlite3.connect("presenca.db")
        conn.execute("INSERT INTO alunos(nome) VALUES(?)", (nome,))
        conn.commit()
        conn.close()

        return f"""
        <h2 align='center'>✅ Aluno cadastrado!</h2>
        <h3 align='center'>{nome}</h3>
        <p align='center'><a href='/'>Voltar</a></p>
        """

    return """
    <html><body style='font-family:Arial;text-align:center;padding:20px'>
    <h2>➕ Cadastro de Alunos</h2>

    <form method='POST'>
        <input type='text' name='nome' required placeholder='Nome do aluno'
               style='padding:12px;width:80%'>
        <br><br>
        <button type='submit'>Salvar</button>
    </form>

    <br>
    <a href='/'>Voltar</a>
    </body></html>
    """

@app.route("/alunos")
def alunos():
    conn = sqlite3.connect("presenca.db")
    dados = conn.execute("SELECT * FROM alunos ORDER BY nome").fetchall()
    conn.close()

    linhas = ""
    for aluno in dados:
        linhas += f"<tr><td>{aluno[0]}</td><td>{aluno[1]}</td></tr>"

    return f"""
    <html><body style='font-family:Arial;text-align:center;padding:20px'>
    <h2>📋 Alunos Cadastrados</h2>

    <table border='1' align='center' cellpadding='10'>
    <tr><th>ID</th><th>Nome</th></tr>
    {linhas}
    </table>

    <br><a href='/'>Voltar</a>
    </body></html>
    """

@app.route("/chamada", methods=["GET", "POST"])
def chamada():
    if request.method == "POST":

        aluno = request.form["aluno"]


agora = datetime.now() - timedelta(hours=3)
        data = agora.strftime("%d/%m/%Y")
        hora = agora.strftime("%H:%M:%S")

        conn = sqlite3.connect("presenca.db")
        conn.execute(
            "INSERT INTO presencas(aluno,data,hora) VALUES(?,?,?)",
            (aluno, data, hora)
        )
        conn.commit()
        conn.close()

        return f"""
        <html><body style='font-family:Arial;text-align:center;padding:20px'>
        <h2>✅ Presença registrada!</h2>
        <h3>{aluno}</h3>
        <p>{data} - {hora}</p>
        <a href='/chamada'>Nova chamada</a>
        <br><br>
        <a href='/'>Voltar</a>
        </body></html>
        """

    return """
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>

    <body style="font-family:Arial;text-align:center;padding:20px;background:#f4f6f9">

        <h2>🎤 Chamada por Voz</h2>

        <p style="color:#0066cc;">
        Use o microfone do teclado do celular para falar o nome do aluno.
        </p>

        <form method="POST">

            <input
                type="text"
                name="aluno"
                placeholder="Nome do aluno"
                required
                style="padding:12px;width:90%;">

            <br><br>

            <button type="submit">
                Registrar Presença
            </button>

        </form>

        <br>

        <a href="/">Voltar</a>

    </body>

    </html>
    """

@app.route("/presencas")
def presencas():
    conn = sqlite3.connect("presenca.db")
    dados = conn.execute(
        "SELECT aluno,data,hora FROM presencas ORDER BY id DESC"
    ).fetchall()
    conn.close()

    linhas = ""
    for item in dados:
        linhas += f"<tr><td>{item[0]}</td><td>{item[1]}</td><td>{item[2]}</td></tr>"

    return f"""
    <html><body style='font-family:Arial;text-align:center;padding:20px'>
    <h2>✅ Presenças Registradas</h2>

    <table border='1' align='center' cellpadding='10'>
    <tr><th>Aluno</th><th>Data</th><th>Hora</th></tr>
    {linhas}
    </table>

    <br><a href='/'>Voltar</a>
    </body></html>
    """

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("presenca.db")
    cur = conn.cursor()

    total_alunos = cur.execute("SELECT COUNT(*) FROM alunos").fetchone()[0]
    total_presencas = cur.execute("SELECT COUNT(*) FROM presencas").fetchone()[0]

    hoje = (datetime.now() -
    timedelta(hours=3)).strftime("%d/%m/%Y")
    presencas_hoje = cur.execute(
        "SELECT COUNT(*) FROM presencas WHERE data=?",
        (hoje,)
    ).fetchone()[0]

    top = cur.execute("""
    SELECT aluno, COUNT(*) total
    FROM presencas
    GROUP BY aluno
    ORDER BY total DESC
    LIMIT 1
    """).fetchone()

    ultima = cur.execute("""
    SELECT aluno,hora
    FROM presencas
    ORDER BY id DESC
    LIMIT 1
    """).fetchone()

    conn.close()

    aluno_top = top[0] if top else "Nenhum"
    total_top = top[1] if top else 0
    ultima_nome = ultima[0] if ultima else "Nenhuma"
    ultima_hora = ultima[1] if ultima else "--:--"

    return f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body{{font-family:Arial;background:#f4f6f9;padding:15px}}
    .grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
    .card,.bloco{{background:white;border-radius:15px;padding:15px;box-shadow:0 2px 8px rgba(0,0,0,.1)}}
    .card{{text-align:center}}
    .numero{{font-size:28px;font-weight:bold;color:#0066cc}}
    .botao{{display:block;text-decoration:none;background:#0066cc;color:white;padding:15px;border-radius:10px;margin-top:10px;text-align:center}}
    </style>
    </head>

    <body>

    <h2 align="center">📊 Dashboard</h2>

    <div class="grid">
        <div class="card"><div>👥 Alunos</div><div class="numero">{total_alunos}</div></div>
        <div class="card"><div>✅ Presenças</div><div class="numero">{total_presencas}</div></div>
        <div class="card"><div>📅 Hoje</div><div class="numero">{presencas_hoje}</div></div>
        <div class="card"><div>🏆 Destaque</div><div>{aluno_top}</div></div>
    </div>

    <div class="bloco">
        <h3>🕒 Última Presença</h3>
        <p><strong>{ultima_nome}</strong><br>{ultima_hora}</p>
    </div>

    <div class="bloco">
        <h3>🏆 Aluno Mais Presente</h3>
        <p>{aluno_top}<br><strong>{total_top} presenças</strong></p>
    </div>

    <a class="botao" href="/relatorio">📑 Relatórios</a>
    <a class="botao" href="/excel">📊 Exportar Excel</a>
    <a class="botao" href="/">⬅ Voltar</a>

    </body>
    </html>
    """

@app.route("/relatorio")
def relatorio():
    conn = sqlite3.connect("presenca.db")
    dados = conn.execute(
        "SELECT aluno,data,hora FROM presencas ORDER BY id DESC"
    ).fetchall()
    conn.close()

    linhas = "".join(
        f"<tr><td>{a}</td><td>{d}</td><td>{h}</td></tr>"
        for a, d, h in dados
    )

    return f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body{{font-family:Arial;background:#f4f6f9;padding:15px}}
    .card{{background:white;padding:15px;border-radius:15px}}
    .tabela-scroll{{max-height:500px;overflow-y:auto}}
    table{{width:100%;border-collapse:collapse}}
    th{{background:#0066cc;color:white;position:sticky;top:0}}
    th,td{{border:1px solid #ddd;padding:10px;text-align:center}}
    </style>
    </head>

    <body>

    <div class="card">
        <h2>📑 Histórico Completo</h2>

        <div class="tabela-scroll">
            <table>
                <tr>
                    <th>Aluno</th>
                    <th>Data</th>
                    <th>Hora</th>
                </tr>
                {linhas}
            </table>
        </div>
    </div>

    </body>
    </html>
    """


@app.route("/excel")
def excel():

    conn = sqlite3.connect("presenca.db")

    dados = conn.execute("""
        SELECT aluno,data,hora
        FROM presencas
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Presencas"

    ws.append(["Aluno", "Data", "Hora"])

    for linha in dados:
        ws.append(linha)

    arquivo = "presencas.xlsx"
    wb.save(arquivo)

    return send_file(arquivo, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
