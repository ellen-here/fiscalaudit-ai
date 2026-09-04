# 🧠 Fase 8 — Relatório em Linguagem Natural

Até aqui o projeto já achava as inconsistências (regras + machine learning), mas o resultado era sempre um monte de CSV. Ótimo pra quem mexe com dados, ruim pra quem só quer saber "e aí, o que eu preciso olhar antes de fechar o mês?".

Então nesta fase eu fiz a parte que junta tudo e escreve um **relatório em português**, do jeito que eu explicaria pra um contador.

---

## A ideia

Pegar os achados das fases anteriores e transformar num texto que qualquer pessoa lê e entende:

- Quantas coisas apareceram e quais são as mais críticas
- As maiores divergências, com nome da empresa e valor
- O que o modelo de anomalias sinalizou
- E, no fim, uma sugestão de por onde começar

Nada de jargão de dado. É pra ser lido por gente que entende de contabilidade, não de Python.

---

## Sobre usar IA (e por que não depender só dela)

O nome da fase é "IA generativa", e a ideia original era jogar os dados numa LLM (tipo GPT) e deixar ela escrever o relatório.

Só que aí eu pensei: se eu depender de uma chave paga da OpenAI, o projeto **para de funcionar** pra quem clonar e não tiver chave. Pra um projeto que eu quero mostrar por aí, isso é ruim.

Então resolvi assim:

- **O relatório é montado no próprio código**, em português, e roda sempre — sem chave, sem custo, sem internet.
- **Se** você tiver uma chave da OpenAI no `.env`, aí ele usa a IA pra dar aquele polimento no texto, deixando mais fluido.

Ou seja: a IA é um "a mais", não uma muleta. O projeto funciona 100% sem ela.

```python
# resumindo a lógica
texto = montar_texto(...)          # sempre roda
texto, usou_ia = refinar_com_ia(texto)  # só se tiver chave
```

---

## Como ficou o relatório

Rodando com os dados de teste, sai um arquivo `relatorio_auditoria.md` assim:

```markdown
# Relatório de Auditoria — FiscalAudit AI

## Resumo

Passei os dados pelas regras de auditoria e pelo modelo de anomalias.
No total, apareceram 465 pontos que valem uma olhada antes do fechamento.

## Divergências de pagamento

Encontrei 23 contas marcadas como pagas onde o valor pago não bate com
o valor original. Somando as diferenças, dá R$ 56.998,59.

As três maiores:
- Conta #330 (Albuquerque): original R$ 46.645,60, pago R$ 39.768,61 ...

## Sugestão de prioridade

1. Resolver as conciliações inconsistentes (são poucas e travam o fechamento)
2. Conferir as divergências de pagamento maiores
...
```

Repara que ele não só lista número — ele **sugere o que fazer** ("vale checar se foi desconto combinado ou erro de digitação") e **prioriza**. É isso que faz diferença no dia a dia.

---

## Detalhe que eu não quis deixar passar

Os valores saem no formato brasileiro de verdade: `R$ 56.998,59`, não `R$ 56,998.59`. Parece bobo, mas relatório financeiro com número no formato errado dá aquela impressão de coisa mal feita. Fiz uma função pequena só pra isso:

```python
def reais(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
```

---

## Como rodar

```bash
python src/ia/gerar_relatorio.py
```

O relatório sai em `data/processed/relatorio_auditoria.md`. Se quiser usar a IA pra refinar, é só colocar a chave no `.env`:

```env
OPENAI_API_KEY=sua_chave_aqui
```

---

## O que vem depois

Com o relatório pronto, faz sentido:

- **Fase 9** — jogar tudo isso num dashboard (Streamlit), pra visualizar sem abrir CSV
- **Fase 10** — empacotar com Docker e fechar a documentação
