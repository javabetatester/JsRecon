import argparse
import os
import sys
import warnings
import re
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from tqdm import tqdm

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
RX_MAIN_SRC = re.compile(r'src=["\']([^"\']*main[^"\']*\.js)["\']', re.I) #AQUI VOCÊ DEFINE A REGEX DA SOURCE OU ARQUIVO QUE VAI PROCURAR
DEFAULT_FILTERS: dict[str, re.Pattern] = {
    "authDomain": re.compile(r'authDomain\s*[:=]\s*["\']([^"\']+)["\']', re.I), #AQUI VOCÊ DEFINE QUAL O CONTEÚDO QUE DESEJA ACHAR NO DOMINIO/LISTA DE DOMINIO QUE VAI IMPORTAR
}

def localizar_main_js(html: str, base: str) -> str | None:
    m = RX_MAIN_SRC.search(html)
    return urljoin(base, m.group(1)) if m else None

def fetch_main_js(url: str, timeout: int) -> str | None:
    try:
        r = requests.get(url, timeout=timeout, verify=False)
        return r.text if r.status_code == 200 else None
    except requests.RequestException:
        return None

def analisar_dominio(dom: str, filters: dict[str, re.Pattern], timeout: int) -> tuple[str, dict[str, str | None]]:
    base = f"https://{dom.strip().rstrip('/')}/"
    try:
        r_html = requests.get(base, timeout=timeout, verify=False)
        if r_html.status_code != 200:
            return 'ignorado', {}
        main_url = localizar_main_js(r_html.text, base)
        if not main_url:
            return 'ignorado', {}
        js_code = fetch_main_js(main_url, timeout)
        if js_code is None:
            return 'ignorado', {}
    except:
        return 'ignorado', {}
    results: dict[str, str | None] = {}
    for name, regex in filters.items():
        m = regex.search(js_code)
        results[name] = m.group(1) if m else None
    return 'processado', results

def main() -> None:
    parser = argparse.ArgumentParser(description="Verifica padrões embutidos no arquivo main.*.js de domínios listados.")
    parser.add_argument("lista", metavar="FICHEIRO", help="arquivo texto com um domínio por linha")
    parser.add_argument("-t", "--timeout", type=int, default=7, help="timeout (seg.) das requisições HTTP (padrão: 7)")
    parser.add_argument("-n", "--threads", type=int, default=10, help="número de threads para execução paralela")
    args = parser.parse_args()
    if not os.path.isfile(args.lista):
        sys.exit(f"[erro] ficheiro '{args.lista}' não encontrado.")
    with open(args.lista, encoding='utf-8') as f:
        dominios = [ln.strip() for ln in f if ln.strip()]
    if not dominios:
        sys.exit("[erro] lista vazia.")
    filters = DEFAULT_FILTERS
    resultados = {name: {'found': [], 'not_found': []} for name in filters}
    ignorados: list[str] = []
    matched_counts = {name: 0 for name in filters}

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_dom = {executor.submit(analisar_dominio, dom, filters, args.timeout): dom for dom in dominios}
        with tqdm(total=len(future_to_dom), unit="domínio", ascii=True) as pbar:
            for future in as_completed(future_to_dom):
                dom = future_to_dom[future]
                try:
                    status, res = future.result()
                except Exception:
                    ignorados.append(dom)
                else:
                    if status != 'processado':
                        ignorados.append(dom)
                    else:
                        for name, val in res.items():
                            if val is not None:
                                resultados[name]['found'].append(f"{dom}: {val}")
                                matched_counts[name] += 1
                            else:
                                resultados[name]['not_found'].append(dom)
                pbar.set_postfix(matched_counts)
                pbar.update(1)

    for name, groups in resultados.items():
        with open(f"{name}_found.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(groups['found']))
        with open(f"{name}_not_found.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(groups['not_found']))
    with open("ignorados.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(ignorados))
    print("\nResumo:")
    for name, groups in resultados.items():
        print(f"  Padrão '{name}': encontrados = {len(groups['found'])}, não encontrados = {len(groups['not_found'])}")
    print(f"  Ignorados (falha ou main.js ausente): {len(ignorados)}")
    print("Arquivos gerados:")
    print(", ".join([f"{name}_found.txt, {name}_not_found.txt" for name in filters] + ["ignorados.txt"]))

if __name__ == "__main__":
    main()
