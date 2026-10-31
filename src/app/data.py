"""Dados do Leroy Cyber Quiz (mockup funcional do Grupo LevelUP).

Os dados ficam em memória: o objetivo desta versão é servir de base para a
esteira DevSecOps, sem depender de banco de dados externo.
"""

PERFIL = {
    "nome": "Marina Costa",
    "saudacao": "Olá, Marina.",
    "contexto": "Painel pessoal · Vendas · Sudeste · São Paulo",
    "pontos": 1240,
    "meta_pontos": 1500,
    "missoes": 12,
    "trofeus": 3,
    "trofeus_total": 7,
    "streak_dias": 5,
    "nivel": "Vigilante",
    "nivel_numero": 7,
    "membro_desde": "mar/2026",
    "continue": {
        "titulo": "Phishing · Intermediário",
        "cenario_id": "rh-urgente",
    },
    "conquistas": ["bronze", "prata", "bronze", None, None, None, None],
}

TRILHAS = [
    {"numero": "01", "nome": "Phishing", "descricao": "E-mails e mensagens enganosas", "salas": 12},
    {"numero": "02", "nome": "Senhas Seguras", "descricao": "Credenciais e mesa limpa", "salas": 8},
    {"numero": "03", "nome": "Engenharia Social", "descricao": "Manipulação e pressão", "salas": 10},
    {"numero": "04", "nome": "LGPD", "descricao": "Proteção de dados", "salas": 9},
    {"numero": "05", "nome": "E-commerce", "descricao": "Fraudes em vendas online", "salas": 11},
    {"numero": "06", "nome": "IA & Riscos", "descricao": "Uso responsável de IA", "salas": 10},
]

NIVEIS_XP = {"Básico": 10, "Intermediário": 20, "Avançado": 30}

CENARIOS = {
    "rh-urgente": {
        "titulo": "O pedido urgente do RH",
        "trilha": "Phishing",
        "nivel": "Intermediário",
        "progresso": "Cenário 3 / 5",
        "remetente": "RH Leroy Merlin",
        "horario": "14:32",
        "mensagem": (
            "Olá! Aqui é a Patrícia do RH. Estamos validando os dados bancários "
            "para o pagamento do PLR de hoje à noite. Preciso que você me envie o "
            "número do seu CPF, agência e conta corrente até as 15h, senão você "
            "pode ficar de fora deste ciclo. É urgente!"
        ),
        "opcoes": {
            "A": {
                "texto": "Envio os dados, é o RH e o PLR é hoje, não posso perder.",
                "xp": 0,
                "correta": False,
                "titulo": "Os dados foram expostos.",
                "consequencia": (
                    "Urgência artificial, ameaça velada e autoridade institucional são as "
                    "três alavancas clássicas do phishing. Dados financeiros nunca devem "
                    "ser enviados por WhatsApp."
                ),
            },
            "B": {
                "texto": "Peço para ela ligar do número fixo do RH para confirmar antes.",
                "xp": 8,
                "correta": False,
                "titulo": "Algo passou despercebido.",
                "consequencia": (
                    "Boa intuição. Mas o ideal é ir além: o número de retorno também pode "
                    "ser falso. O canal oficial é o portal interno."
                ),
            },
            "C": {
                "texto": "Reporto a mensagem pelo canal interno e não respondo.",
                "xp": 20,
                "correta": True,
                "titulo": "Decisão exemplar.",
                "consequencia": (
                    "Reportar permite que o time de segurança alerte os demais colaboradores "
                    "sobre a campanha em circulação."
                ),
            },
            "D": {
                "texto": "Bloqueio o número e sigo trabalhando.",
                "xp": 10,
                "correta": False,
                "titulo": "Quase lá.",
                "consequencia": (
                    "Bloquear protege você, mas a empresa não fica sabendo que o ataque "
                    "está circulando. Reportar é essencial."
                ),
            },
        },
    },
    "rastreio-falso": {
        "titulo": "O rastreio que não existe",
        "trilha": "E-commerce",
        "nivel": "Básico",
        "progresso": "Cenário 1 / 5",
        "remetente": "Transportadora",
        "horario": "09:10",
        "mensagem": (
            "Sua encomenda está retida por uma taxa de R$ 4,90. Regularize hoje em "
            "entrega-rapida-seguro.example/taxa para evitar a devolução ao remetente."
        ),
        "opcoes": {
            "A": {
                "texto": "Pago a taxa, é um valor baixo.",
                "xp": 0,
                "correta": False,
                "titulo": "Golpe consumado.",
                "consequencia": (
                    "O valor baixo é a isca: a página captura dados de cartão. Cobranças "
                    "legítimas não chegam por links encurtados ou domínios desconhecidos."
                ),
            },
            "B": {
                "texto": "Confiro o código de rastreio no site oficial da transportadora.",
                "xp": 10,
                "correta": True,
                "titulo": "Boa verificação.",
                "consequencia": (
                    "Acessar o site oficial digitando o endereço evita o link malicioso."
                ),
            },
            "C": {
                "texto": "Encaminho a mensagem para colegas perguntando se já receberam.",
                "xp": 2,
                "correta": False,
                "titulo": "Cuidado ao espalhar.",
                "consequencia": (
                    "Encaminhar o golpe amplia o alcance. Prefira reportar ao canal interno."
                ),
            },
        },
    },
    "contrato-ia": {
        "titulo": "O contrato no assistente de IA",
        "trilha": "IA & Riscos",
        "nivel": "Avançado",
        "progresso": "Cenário 2 / 5",
        "remetente": "Você",
        "horario": "16:45",
        "mensagem": (
            "Você precisa resumir um contrato com um fornecedor antes da reunião de "
            "amanhã. Uma ferramenta de IA pública faria isso em segundos."
        ),
        "opcoes": {
            "A": {
                "texto": "Colo o contrato inteiro na ferramenta de IA pública.",
                "xp": 0,
                "correta": False,
                "titulo": "Dados sensíveis expostos.",
                "consequencia": (
                    "Contratos contêm informações confidenciais. Ferramentas públicas podem "
                    "reter o conteúdo enviado."
                ),
            },
            "B": {
                "texto": "Uso apenas a ferramenta de IA homologada pela empresa.",
                "xp": 30,
                "correta": True,
                "titulo": "Julgamento seguro.",
                "consequencia": (
                    "Ferramentas homologadas têm acordos de confidencialidade e controles "
                    "de retenção definidos pela empresa."
                ),
            },
            "C": {
                "texto": "Removo os nomes, mas colo o restante na ferramenta pública.",
                "xp": 10,
                "correta": False,
                "titulo": "Anonimização incompleta.",
                "consequencia": (
                    "Valores, cláusulas e prazos ainda identificam o negócio. Anonimizar "
                    "só nomes não basta."
                ),
            },
        },
    },
}
