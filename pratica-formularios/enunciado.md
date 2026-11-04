# Prática — Formulários com Flask

## Inscrição no Hackathon IFPB

Você vai construir, usando **apenas Flask** (sem Flask-WTF ou outras extensões), o sistema de inscrição de um hackathon fictício. O objetivo é praticar os **diversos tipos de campos de formulário HTML** e o **recebimento dos dados via `POST`** com o objeto `request`.

Ao final, o participante preenche o formulário, envia, e o servidor exibe uma página de confirmação com todos os dados recebidos, já convertidos e validados.

---

## Objetivos de aprendizagem

- Criar formulários com `method="POST"` e `action` apontando para uma rota Flask
- Entender a relação entre o atributo `name` do campo HTML e a chave em `request.form`
- Usar `request.form.get()`, `request.form.getlist()` e `request.files`
- Converter os valores recebidos (tudo chega como **string**!) para `int`, `float`, `date`, `bool`
- Fazer validações simples no servidor e devolver mensagens de erro
- Reexibir os valores já digitados quando houver erro

---

## Estrutura do projeto

```
pratica-formularios/
├── app.py
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── inscricao.html
    └── confirmacao.html
```

Use o mesmo `venv` / `requirements.txt` do projeto `flask-exemplos`.

---

## Revisão rápida: como os dados chegam no Flask

```python
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/inscricao', methods=['GET', 'POST'])
def inscricao():
    if request.method == 'POST':
        nome = request.form.get('nome')               # um único valor (str ou None)
        linguagens = request.form.getlist('linguagens')  # vários valores (lista de str)
        foto = request.files.get('foto')              # arquivo enviado (FileStorage)
        ...
    return render_template('inscricao.html')
```

| Situação | Como ler no Flask | O que chega |
|---|---|---|
| Campo de texto preenchido | `request.form.get('campo')` | `'texto digitado'` |
| Campo de texto vazio | `request.form.get('campo')` | `''` (string vazia) |
| Campo ausente / checkbox desmarcado | `request.form.get('campo')` | `None` |
| Checkbox marcado sem `value` | `request.form.get('campo')` | `'on'` |
| Vários campos com o mesmo `name` | `request.form.getlist('campo')` | `['a', 'b']` |
| `<select multiple>` | `request.form.getlist('campo')` | `['a', 'b']` |
| `<input type="file">` | `request.files.get('campo')` | objeto `FileStorage` |

> ⚠️ `request.form['campo']` (com colchetes) gera erro **400 Bad Request** se o campo não existir. Prefira `.get()`.

---

## Parte 1 — O formulário (`templates/inscricao.html`)

Crie a rota `GET /inscricao` que renderiza o formulário. O `<form>` deve usar:

```html
<form method="POST" action="{{ url_for('inscricao') }}" enctype="multipart/form-data">
```

> O `enctype="multipart/form-data"` é **obrigatório** para enviar arquivos. Sem ele, `request.files` vem vazio.

Organize os campos em `<fieldset>` com `<legend>`, e **todo campo deve ter um `<label for="...">`**.

### Fieldset 1 — Dados pessoais

| Campo | Tipo HTML | `name` | Regras no HTML |
|---|---|---|---|
| Nome completo | `<input type="text">` | `nome` | `required`, `minlength="3"` |
| E-mail | `<input type="email">` | `email` | `required` |
| Senha | `<input type="password">` | `senha` | `required`, `minlength="6"` |
| Confirmar senha | `<input type="password">` | `confirma_senha` | `required` |
| Data de nascimento | `<input type="date">` | `nascimento` | `required` |
| Telefone | `<input type="tel">` | `telefone` | `placeholder="(83) 90000-0000"` |
| Gênero | `<input type="radio">` (3 opções: Feminino, Masculino, Prefiro não informar) | `genero` | uma opção marcada por padrão |

### Fieldset 2 — Perfil técnico

| Campo | Tipo HTML | `name` | Detalhes |
|---|---|---|---|
| Curso | `<select>` | `curso` | Opções: TSI, Engenharia de Computação, Redes, Outro |
| Período | `<input type="number">` | `periodo` | `min="1"`, `max="10"` |
| Nível de experiência | `<input type="range">` | `experiencia` | `min="0"`, `max="10"`, `step="1"` |
| Linguagens que domina | `<input type="checkbox">` (vários com o **mesmo `name`**) | `linguagens` | Python, JavaScript, Java, C, PHP, Go |
| Áreas de interesse | `<select multiple>` | `areas` | Web, Mobile, IA, Jogos, Segurança, Dados |
| GitHub / Portfólio | `<input type="url">` | `github` | opcional |

### Fieldset 3 — Hackathon

| Campo | Tipo HTML | `name` | Detalhes |
|---|---|---|---|
| Tamanho da camiseta | `<input type="radio">` | `camiseta` | P, M, G, GG |
| Cor favorita (para o crachá) | `<input type="color">` | `cor_cracha` | valor padrão `#3b82f6` |
| Horário de chegada | `<input type="time">` | `chegada` | |
| Restrição alimentar | `<input type="text">` com `<datalist>` | `restricao` | sugestões: Nenhuma, Vegetariana, Vegana, Sem glúten, Sem lactose |
| Foto para o crachá | `<input type="file">` | `foto` | `accept="image/*"` |
| Por que você quer participar? | `<textarea>` | `motivacao` | `rows="5"`, `maxlength="500"` |

### Fieldset 4 — Termos

| Campo | Tipo HTML | `name` | Detalhes |
|---|---|---|---|
| Aceito o regulamento | `<input type="checkbox">` (único) | `aceite` | `required` |
| Quero receber novidades por e-mail | `<input type="checkbox">` (único) | `newsletter` | opcional, **com** `value="sim"` |
| Código do evento | `<input type="hidden">` | `evento_id` | `value="HACK-2026"` |

Por fim, dois botões: `<button type="submit">Enviar inscrição</button>` e `<button type="reset">Limpar</button>`.

---

## Parte 2 — Recebendo os dados (`POST /inscricao`)

Na mesma rota, quando `request.method == 'POST'`, leia **todos** os campos e monte um dicionário `dados`. Atenção às conversões:

| Campo | Conversão esperada |
|---|---|
| `periodo` | `int` |
| `experiencia` | `int` |
| `nascimento` | `datetime.date` (dica: `date.fromisoformat(...)`) → calcule a **idade** |
| `linguagens`, `areas` | `list` (use `getlist`) |
| `aceite`, `newsletter` | `bool` (marcado → `True`, desmarcado → `False`) |
| `foto` | guarde apenas o **nome do arquivo** (`foto.filename`) |
| `senha`, `confirma_senha` | **não** devem ir para a página de confirmação! |

Exemplo de leitura com conversão segura:

```python
periodo_txt = request.form.get('periodo', '')
periodo = int(periodo_txt) if periodo_txt.isdigit() else None
```

---

## Parte 3 — Validação no servidor

A validação do HTML (`required`, `minlength`...) pode ser burlada (DevTools, `curl`, etc.). Por isso, **valide também no Flask**. Crie uma lista `erros` e adicione uma mensagem para cada regra violada:

1. `nome` com menos de 3 caracteres
2. `email` sem `@`
3. `senha` com menos de 6 caracteres
4. `senha` diferente de `confirma_senha`
5. Idade menor que 16 anos
6. `periodo` fora do intervalo 1–10
7. Nenhuma linguagem selecionada
8. `aceite` não marcado
9. `motivacao` com mais de 500 caracteres

- **Se houver erros:** renderize `inscricao.html` novamente, exibindo a lista de erros no topo e **mantendo os valores já preenchidos** (exceto as senhas).
- **Se não houver erros:** renderize `confirmacao.html` passando o dicionário `dados`.

Dica para manter os valores preenchidos — passe `request.form` para o template:

```python
return render_template('inscricao.html', erros=erros, form=request.form)
```

```html
<input type="text" id="nome" name="nome" value="{{ form.get('nome', '') }}">

<input type="radio" name="camiseta" value="M"
       {% if form.get('camiseta') == 'M' %}checked{% endif %}>

<input type="checkbox" name="linguagens" value="Python"
       {% if 'Python' in form.getlist('linguagens') %}checked{% endif %}>

<option value="TSI" {% if form.get('curso') == 'TSI' %}selected{% endif %}>TSI</option>
```

> Para que isso funcione também no `GET`, envie `form=request.form` nos dois casos (no `GET` ele vem vazio). Não use `form={}`: um `dict` comum não tem o método `getlist`.

---

## Parte 4 — Página de confirmação (`templates/confirmacao.html`)

Exiba os dados recebidos de forma organizada:

- Um "crachá" (`<div>`) com o nome do participante e **a borda/fundo na cor escolhida** em `cor_cracha` (use `style="border-color: {{ dados.cor_cracha }}"`)
- Uma tabela ou `<dl>` com todos os demais campos
- A idade calculada (ex.: "20 anos")
- As linguagens e áreas como **listas `<ul>`** geradas com `{% for %}`
- O nível de experiência mostrado também como uma `<progress value="..." max="10">`
- Newsletter: exiba "Sim" ou "Não" com `{% if %}`
- Se o GitHub não foi informado, exiba "Não informado"
- Um link "Fazer nova inscrição" de volta para `url_for('inscricao')`

---

## Parte 5 — Estilização (`static/style.css`)

Aplique o que vimos nas aulas de CSS:

- Formulário centralizado com `max-width`
- `fieldset` com borda arredondada e espaçamento interno
- Campos empilhados (`display: flex; flex-direction: column` ou `grid`)
- Destaque visual em `:focus` e em `:invalid`
- Caixa de erros com fundo vermelho claro

---

## Desafios extras (opcionais)

1. **Salvar a foto:** use `foto.save(os.path.join('static/uploads', secure_filename(foto.filename)))` (importe `secure_filename` de `werkzeug.utils`) e mostre a imagem no crachá.
2. **Lista de inscritos:** guarde cada inscrição válida em uma lista global `inscritos` e crie a rota `GET /inscritos` exibindo uma tabela com todos.
3. **Padrão PRG (Post/Redirect/Get):** após uma inscrição válida, use `redirect(url_for('confirmacao', id=...))` em vez de renderizar direto. Teste: o que acontece ao apertar F5 em cada versão?
4. **GET × POST:** crie um formulário de **busca** em `/inscritos` com `method="GET"` que filtre por curso. Leia o valor com `request.args.get('curso')` e observe a diferença na URL.
5. **Inspecionar a requisição:** abra o DevTools → aba *Network*, envie o formulário e localize o *Payload* da requisição `POST`. Compare com `print(request.form)` no terminal.

---

## Checklist de entrega

- [ ] Rota `/inscricao` aceita `GET` e `POST`
- [ ] Formulário usa pelo menos **15 tipos diferentes** de campo/elemento (`text`, `email`, `password`, `date`, `tel`, `radio`, `select`, `number`, `range`, `checkbox` múltiplo, `select multiple`, `url`, `color`, `time`, `datalist`, `file`, `textarea`, `checkbox` único, `hidden`)
- [ ] Todos os campos têm `<label>` associado
- [ ] Dados lidos com `request.form.get`, `request.form.getlist` e `request.files`
- [ ] Conversões de tipo feitas corretamente (`int`, `date`, `bool`, `list`)
- [ ] Validações no servidor com mensagens de erro
- [ ] Valores preenchidos são mantidos quando há erro
- [ ] Senhas **não** aparecem na confirmação
- [ ] Página de confirmação exibe todos os dados formatados
- [ ] CSS aplicado
