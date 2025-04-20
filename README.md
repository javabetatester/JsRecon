# JSRecon

**Ferramenta de reconnaissance para extração de padrões em arquivos `main*.js` de múltiplos domínios.**

---

## 📌 Requisitos

- Python **3.8** ou superior
- Módulos Python:
    - `requests`
    - `tqdm`

> Instale-os via `pip install -r requirements.txt`.

---

## 🚀 Instalação

1. Clone o repositório ou copie `jsrecon.py` para sua máquina:
   ```bash
   git clone https://github.com/seu-usuario/jsrecon.git
   cd jsrecon
   ```

2. (Opcional, mas recomendado) Crie e ative um ambiente virtual:
   ```bash
   python3 -m venv .venv
   # Linux/macOS
   source .venv/bin/activate
   # Windows
   .venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Uso

```bash
python jsrecon.py DOMAINS.txt [opções]
```

- `DOMAINS.txt`  : arquivo texto com um domínio por linha (ex.: `example.com`).
- `-t, --timeout`: timeout em segundos para requisições HTTP (padrão: 7).
- `-n, --threads`: número de threads concorrentes (padrão: 10).

### Exemplo

1. Crie um arquivo `domains.txt`:
   ```bash
   echo "example.com" > domains.txt
   echo "another.com" >> domains.txt
   ```
2. Execute o script:
   ```bash
   python jsrecon.py domains.txt -t 5 -n 20
   ```

---

## 📂 Saída

- Para cada filtro definido (em `DEFAULT_FILTERS`), serão gerados dois arquivos:
    - `<filtro>_found.txt`     : lista de `domínio: valor` encontrados.
    - `<filtro>_not_found.txt`: lista de domínios sem correspondência.
- `ignorados.txt`            : domínios que deram erro ou não expõem `main.js`.
- No console, um resumo dos totais processados.

---

## ⚙️ Personalização

1. **Regex de detecção de `main.js`**
    - Em `RX_MAIN_SRC`, ajuste a expressão para capturar o nome/caminho desejado.

2. **Filtros de extração**
    - Em `DEFAULT_FILTERS`, adicione ou modifique pares `nome: re.Pattern` para outros padrões no JS.

3. **Timeout e Threads**
    - Ajuste dinamicamente via CLI (`-t`, `-n`).

---

## 📁 Estrutura do Projeto

```
jsrecon/
├── jsrecon.py         # Script principal
├── requirements.txt   # Dependências Python
├── domains.txt        # Arquivo de exemplo de domínios
└── README.md          # Documentação (este arquivo)
```

---

## 📝 Licença

Este projeto está licenciado sob a **MIT License**.

