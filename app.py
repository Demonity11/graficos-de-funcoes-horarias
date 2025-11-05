from flask import Flask, render_template, request, session, url_for, redirect
from os import environ, getenv
from dotenv import load_dotenv
from math import ceil

load_dotenv(dotenv_path="settings.env")

app = Flask(__name__)
app.config['SECRET_KEY'] = getenv("SECRET_KEY")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.route("/historico", methods=["GET", "POST"])
def historico():
    if not session.get("historico"):
        session["historico"] = []

    return render_template("historico.html", historico=session["historico"])


@app.route("/posicao")
def posicao():
    return render_template("posicao.html")


@app.route("/velocidade")
def velocidade():
    return render_template("velocidade.html")


@app.route("/espaco")
def espaco():
    return render_template("espaco.html")


@app.route("/result", methods=["POST"])
def result():
    if not session.get("historico"):
        session["historico"] = []

    equacao = ""
    data = []
    seletor_unidade = request.form.get("seletor_unidade")

    if not seletor_unidade:
        unidade = ["m", "s"]
    else:
        unidade = ["km", "h"]

    #caso o tempo seja omitido de alguma forma, há um valor padrão
    tempo = [_ for _ in range(11)]
    label = [str(_)+unidade[1] for _ in range(11)]

    #criação do eixo do tempo no gráfico + tratamento de valores com vírgula
    t = request.form.get("t")
    if t:
        if "," in t:
            t = t.replace(",", ".")

        if "-" in t:
            t = t[1::]

        t_arredondado = ceil(float(t))
        label = [str(_)+unidade[1] for _ in range(0, t_arredondado)]
        tempo = [_ for _ in range(0, t_arredondado)]

        label.append(t+unidade[1])
        tempo.append(float(t))

    #tratamento dos valores para que o python possa ler sem problemas
    s0 = request.form.get("s0")
    if s0:
        if "," in s0:
            s0 = s0.replace(",", ".")
    
    ac = request.form.get("ac")
    if ac:
        if "," in ac:
            ac = ac.replace(",", ".")

    v0 = request.form.get("v0")
    if v0:
        if "," in v0:
            v0 = v0.replace(",", ".")

    v = request.form.get("v")
    if v:
        if "," in v:
            v = v.replace(",", ".")

    #condição para determinação de qual equação estamos trabalhando + construção do eixo y que pode ser
    #espaço, velocidade ou posição.
    if ac and s0 and v0:
        equacao = "Espaço"
        session["historico"].append([equacao, [s0, v0, ac, t]])
        session.modified = True

        for t in tempo:
            v0Xt = float(v0)*t
            acXt2 = (float(ac)/2)*t**2
            data.append(float(s0) + v0Xt + acXt2)

    elif ac and v0:
        equacao = "Velocidade"
        session["historico"].append([equacao, [v0, ac, t]])
        session.modified = True

        for t in tempo:
            acXt = float(ac)*t
            data.append(float(v0)+ acXt)
    
    elif v:
        equacao = "Posição"
        session["historico"].append([equacao, [s0, v, t]])
        session.modified = True

        for t in tempo:
            vXt = float(v)*t
            data.append(float(s0) + vXt)

    return render_template("result.html", label=label, data=data, equacao=equacao, unidade=unidade)


@app.route("/limpar_historico", methods=["POST"]) # Use POST para ações que modificam o estado
def limpar_historico():
    # Verifique se a chave 'historico' existe na sessão antes de tentar limpar
    if "historico" in session:
        del session["historico"] # Remove a chave 'historico' da sessão
    # Redirecione o usuário de volta para a página do histórico ou outra página
    return redirect(url_for("historico")) # Redireciona para a rota 'historico'


#essa rota serve para lidar com erros que só vão acontecer caso tentem editar o html
@app.errorhandler(500)
def error_page(error):
    return render_template("error.html"), 500


if __name__ == "__main__":
    app.run(debug=True)