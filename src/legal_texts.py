# -*- coding: utf-8 -*-
"""Mapeamento e recuperação do teor literal dos dispositivos legais da

Instrução Normativa GABSEC/SENAPPEN/MJSP nº 75/2026 para cada uma das
30 perguntas da metodologia de Parâmetros Mínimos para Ouvidorias de Serviços Penais.
"""
from __future__ import annotations

# Mapeamento chave de ocorrência (sheet_name:question_code) -> teor literal do dispositivo
LEGAL_TEXTS: dict[str, str] = {
    # -------------------------------------------------------------------------
    # 01_Institucionalização
    # -------------------------------------------------------------------------
    "01_Institucionalização:M1-11": (
        "Art. 6º A criação da Ouvidoria de Serviços Penais será formalizada por meio de ato "
        "normativo específico expedido pela autoridade competente do respectivo ente federativo."
    ),

    # -------------------------------------------------------------------------
    # 02_Autonomia
    # -------------------------------------------------------------------------
    "02_Autonomia:M3-56": (
        "Art. 4º A criação e a estruturação das Ouvidorias de Serviços Penais observarão, no mínimo, os seguintes parâmetros:\n"
        "I - autonomia técnica e funcional, assegurada a independência na análise e no encaminhamento das manifestações;\n\n"
        "Art. 6º, § 1º O ato de criação disporá, no mínimo, sobre:\n"
        "I - a vinculação administrativa da unidade, preferencialmente ao dirigente máximo do órgão gestor "
        "do sistema penal, de modo a assegurar autonomia técnica e legitimidade institucional."
    ),
    "02_Autonomia:M3-57": (
        "Art. 4º A criação e a estruturação das Ouvidorias de Serviços Penais observarão, no mínimo, os seguintes parâmetros:\n"
        "I - autonomia técnica e funcional, assegurada a independência na análise e no encaminhamento das manifestações;\n\n"
        "Art. 8º A Ouvidoria de Serviços Penais será coordenada por um Ouvidor, nomeado pela autoridade máxima "
        "do órgão gestor do sistema penal."
    ),
    "02_Autonomia:M1-12": (
        "Art. 6º, § 1º O ato de criação disporá, no mínimo, sobre:\n"
        "III - o dever de colaboração das áreas técnicas e administrativas do órgão quanto às demandas encaminhadas pela Ouvidoria;\n\n"
        "Art. 10. À Ouvidoria de Serviços Penais (...) compete:\n"
        "II - solicitar informações, documentos e, quando necessário, a apuração dos fatos às áreas técnicas competentes "
        "do órgão, que deverão responder nos prazos estabelecidos."
    ),
    "02_Autonomia:M4-67": (
        "Art. 13. O funcionamento da Ouvidoria de Serviços Penais observará fluxo simples e objetivo para "
        "o tratamento das manifestações, conforme representação gráfica constante no Anexo VIII, compreendendo, no mínimo:\n"
        "I - recebimento da manifestação pelos canais disponíveis;\n"
        "II - registro em meio eletrônico ou sistema adotado pelo ente federativo;\n"
        "III - encaminhamento à área competente para análise do conteúdo;\n"
        "IV - acompanhamento da resposta pela Ouvidoria; e\n"
        "V - devolutiva ao usuário, quando aplicável."
    ),
    "02_Autonomia:M4-68": (
        "Art. 6º, § 1º O ato de criação disporá, no mínimo, sobre:\n"
        "IV - os prazos para manifestação das áreas competentes e para devolutiva ao usuário;\n\n"
        "Art. 10. À Ouvidoria de Serviços Penais (...) compete:\n"
        "II - solicitar informações, documentos e, quando necessário, a apuração dos fatos às áreas técnicas competentes do órgão, "
        "que deverão responder nos prazos estabelecidos;\n"
        "IV - assegurar resposta ao manifestante quanto às providências adotadas em relação à sua demanda, em linguagem clara, objetiva e respeitosa;\n\n"
        "Art. 13. O funcionamento da Ouvidoria de Serviços Penais observará fluxo simples e objetivo (...), compreendendo, no mínimo:\n"
        "IV - acompanhamento da resposta pela Ouvidoria; e\n"
        "V - devolutiva ao usuário, quando aplicável."
    ),

    # -------------------------------------------------------------------------
    # 03_Imparcialidade
    # -------------------------------------------------------------------------
    "03_Imparcialidade:M4-69": (
        "Art. 4º A criação e a estruturação das Ouvidorias de Serviços Penais observarão, no mínimo, os seguintes parâmetros:\n"
        "II - imparcialidade, com resguardo da identidade dos denunciantes, sempre que solicitado ou necessário;\n"
        "§ 2º Será garantido o sigilo do conteúdo das informações recebidas quando imprescindível à segurança da sociedade "
        "e do Estado ou à proteção de direitos fundamentais, nos termos do art. 5º, inciso XXXIII, da Constituição Federal, "
        "e da Lei nº 12.527, de 18 de novembro de 2011.\n\n"
        "Art. 10. À Ouvidoria de Serviços Penais (...) compete:\n"
        "III - assegurar a proteção da identidade do manifestante, garantindo o sigilo da fonte sempre que solicitado "
        "ou quando a natureza da informação assim o exigir."
    ),
    "03_Imparcialidade:M3-63": (
        "Art. 9º, § 4º Todos os servidores e colaboradores lotados na Ouvidoria deverão assinar Termo de Compromisso "
        "de Manutenção de Sigilo Funcional, conforme modelo constante no Anexo VI desta Instrução Normativa, antes do início de suas atividades."
    ),

    # -------------------------------------------------------------------------
    # 04_Acessibilidade
    # -------------------------------------------------------------------------
    "04_Acessibilidade:M2-41": (
        "Art. 7º, § 2º A Ouvidoria de Serviços Penais deverá disponibilizar canais institucionais de comunicação, "
        "assegurando amplo acesso da sociedade, no mínimo:\n"
        "I - endereço eletrônico exclusivo, com domínio institucional."
    ),
    "04_Acessibilidade:M2-43": (
        "Art. 7º, § 2º A Ouvidoria de Serviços Penais deverá disponibilizar canais institucionais de comunicação, "
        "assegurando amplo acesso da sociedade, no mínimo:\n"
        "II - linha telefônica funcional, de uso restrito à equipe da Ouvidoria, inclusive ramal exclusivo."
    ),
    "04_Acessibilidade:M2-47": (
        "Art. 7º, § 2º A Ouvidoria de Serviços Penais deverá disponibilizar canais institucionais de comunicação, "
        "assegurando amplo acesso da sociedade, no mínimo:\n"
        "IV - endereço físico para recebimento de correspondências."
    ),
    "04_Acessibilidade:M2-16": (
        "Art. 7º, § 1º A Ouvidoria de Serviços Penais disporá de infraestrutura física e institucional mínima, compreendendo:\n"
        "I - instalação física própria, em ambiente que assegure privacidade, sigilo, acessibilidade e condições adequadas de trabalho;\n"
        "II - espaço reservado para atendimento presencial, equipado de forma a garantir a confidencialidade das informações e o atendimento humanizado."
    ),
    "04_Acessibilidade:M1-13": (
        "Art. 4º A criação e a estruturação das Ouvidorias de Serviços Penais observarão, no mínimo, os seguintes parâmetros:\n"
        "III - acessibilidade e atendimento humanizado, com a disponibilização de canais adequados aos servidores, ao usuário, "
        "inclusive à pessoa privada de liberdade em cumprimento de pena ou de medida alternativa ao cárcere, bem como aos egressos e seus familiares;\n\n"
        "Art. 10. À Ouvidoria de Serviços Penais (...) compete:\n"
        "I - receber, analisar, tratar e encaminhar manifestações apresentadas por servidores, usuários, inclusive pessoas privadas "
        "de liberdade em cumprimento de pena ou de medida alternativa ao cárcere, bem como por egressos e seus familiares, tais como: "
        "a) denúncias; b) reclamações; c) solicitações; d) sugestões; e e) elogios."
    ),
    "04_Acessibilidade:M4-64": (
        "Art. 4º A criação e a estruturação das Ouvidorias de Serviços Penais observarão, no mínimo, os seguintes parâmetros:\n"
        "III - acessibilidade e atendimento humanizado, com a disponibilização de canais adequados aos servidores, ao usuário, "
        "inclusive à pessoa privada de liberdade em cumprimento de pena ou de medida alternativa ao cárcere, bem como aos egressos e seus familiares;\n\n"
        "Art. 10. À Ouvidoria de Serviços Penais (...) compete:\n"
        "I - receber, analisar, tratar e encaminhar manifestações apresentadas por servidores, usuários, inclusive pessoas privadas "
        "de liberdade em cumprimento de pena ou de medida alternativa ao cárcere, bem como por egressos e seus familiares, tais como: "
        "a) denúncias; b) reclamações; c) solicitações; d) sugestões; e e) elogios."
    ),

    # -------------------------------------------------------------------------
    # 05_Transparência
    # -------------------------------------------------------------------------
    "05_Transparência:M2-35": (
        "Art. 4º A criação e a estruturação das Ouvidorias de Serviços Penais observarão, no mínimo, os seguintes parâmetros:\n"
        "IV - transparência e publicidade, mediante a divulgação dos canais de atendimento e das ações desenvolvidas;\n\n"
        "Art. 7º, § 6º Para apoio às atividades da Ouvidoria de Serviços Penais, recomenda-se que o ente federativo disponibilize recursos administrativos e operacionais, tais como:\n"
        "III - instrumentos de divulgação institucional, compreendendo, no mínimo: a) placas de sinalização; b) cartazes informativos; c) cartões com os contatos da Ouvidoria; e d) materiais informativos de caráter educativo."
    ),
    "05_Transparência:M4-71": (
        "Art. 4º A criação e a estruturação das Ouvidorias de Serviços Penais observarão, no mínimo, os seguintes parâmetros:\n"
        "IV - transparência e publicidade, mediante a divulgação dos canais de atendimento e das ações desenvolvidas;\n\n"
        "Art. 10. À Ouvidoria de Serviços Penais (...) compete:\n"
        "VI - elaborar e publicar relatórios periódicos de atividades, observados a estrutura mínima e os indicadores de desempenho "
        "estabelecidos no Anexo VII, contendo dados estatísticos sobre as demandas recebidas e os resultados alcançados, resguardadas as informações de natureza sigilosa;\n\n"
        "Art. 12, § 3º A Ouvidoria deverá elaborar relatório de gestão anual, observado o disposto na Lei nº 13.460, de 26 de junho de 2017, em especial no seu Capítulo IV."
    ),

    # -------------------------------------------------------------------------
    # 06_Integração Tec
    # -------------------------------------------------------------------------
    "06_Integração Tec:M2-45": (
        "Art. 4º A criação e a estruturação das Ouvidorias de Serviços Penais observarão, no mínimo, os seguintes parâmetros:\n"
        "V - integração tecnológica, mediante uso preferencial da Plataforma Fala.BR – Sistema Integrado de Ouvidoria e Acesso à Informação, mantida pela Controladoria-Geral da União.\n\n"
        "Art. 7º, § 2º A Ouvidoria de Serviços Penais deverá disponibilizar canais institucionais de comunicação (...), no mínimo:\n"
        "III - formulário eletrônico para registro de manifestações, preferencialmente hospedado na Plataforma Fala.BR;\n\n"
        "Art. 7º, § 4º A Ouvidoria de Serviços Penais disporá de recursos tecnológicos e de segurança da informação (...), compreendendo, no mínimo:\n"
        "II - sistemas ou ferramentas que assegurem controle, rastreabilidade, sigilo e acompanhamento das manifestações recebidas;\n\n"
        "Art. 7º, § 5º Enquanto não houver adesão à Plataforma Fala.BR, as manifestações deverão ser registradas em sistema próprio ou em planilha controlada, asseguradas a atribuição de número de protocolo, a rastreabilidade e a confidencialidade das informações."
    ),
    "06_Integração Tec:M4-66": (
        "Art. 11. Toda manifestação recebida pela ouvidoria deverá ser registrada e classificada, com a geração de número de protocolo a ser fornecido ao manifestante para fins de acompanhamento.\n\n"
        "Art. 13. O funcionamento da Ouvidoria de Serviços Penais observará fluxo simples e objetivo para o tratamento das manifestações (...), compreendendo, no mínimo:\n"
        "II - registro em meio eletrônico ou sistema adotado pelo ente federativo."
    ),
    "06_Integração Tec:M2-37": (
        "Art. 4º, § 2º Será garantido o sigilo do conteúdo das informações recebidas quando imprescindível à segurança da sociedade e do Estado ou à proteção de direitos fundamentais (...);\n\n"
        "Art. 7º, § 4º A Ouvidoria de Serviços Penais disporá de recursos tecnológicos e de segurança da informação (...), compreendendo, no mínimo:\n"
        "II - sistemas ou ferramentas que assegurem controle, rastreabilidade, sigilo e acompanhamento das manifestações recebidas;\n"
        "III - mecanismos de segurança da informação, tais como antivírus institucional, autenticação de usuários e controle de acesso aos dados;\n\n"
        "Art. 7º, § 5º Enquanto não houver adesão à Plataforma Fala.BR, as manifestações deverão ser registradas em sistema próprio ou em planilha controlada, asseguradas a atribuição de número de protocolo, a rastreabilidade e a confidencialidade das informações."
    ),
    "06_Integração Tec:M2-17": (
        "Art. 7º, § 4º A Ouvidoria de Serviços Penais disporá de recursos tecnológicos e de segurança da informação (...), compreendendo, no mínimo:\n"
        "I - computadores com acesso seguro à internet e aos sistemas corporativos, destinados ao registro, ao acompanhamento, à análise e ao tratamento das manifestações."
    ),
    "06_Integração Tec:M2-19": (
        "Art. 7º, § 6º Para apoio às atividades da Ouvidoria de Serviços Penais, recomenda-se que o ente federativo disponibilize recursos administrativos e operacionais, tais como:\n"
        "I - impressora multifuncional para emissão de documentos internos, relatórios e comunicações oficiais."
    ),
    "06_Integração Tec:M2-21": (
        "Art. 7º, § 6º Para apoio às atividades da Ouvidoria de Serviços Penais, recomenda-se que o ente federativo disponibilize recursos administrativos e operacionais, tais como:\n"
        "I - impressora multifuncional para emissão de documentos internos, relatórios e comunicações oficiais.\n"
        "(Nota: A IN nº 75/2026 prevê expressamente o equipamento multifuncional; o scanner autônomo não é citado de modo isolado na norma)."
    ),
    "06_Integração Tec:M2-27": (
        "Art. 7º, § 6º Para apoio às atividades da Ouvidoria de Serviços Penais, recomenda-se que o ente federativo disponibilize recursos administrativos e operacionais, tais como:\n"
        "IV - telefone móvel institucional e, quando necessário, veículo para deslocamento da equipe nas atividades externas."
    ),

    # -------------------------------------------------------------------------
    # 07_Maturidade
    # -------------------------------------------------------------------------
    "07_Maturidade:M2-46": (
        "Art. 4º A criação e a estruturação das Ouvidorias de Serviços Penais observarão, no mínimo, os seguintes parâmetros:\n"
        "V - integração tecnológica, mediante uso preferencial da Plataforma Fala.BR – Sistema Integrado de Ouvidoria e Acesso à Informação, mantida pela Controladoria-Geral da União.\n\n"
        "Art. 7º, § 2º A Ouvidoria de Serviços Penais deverá disponibilizar canais institucionais de comunicação (...), no mínimo:\n"
        "III - formulário eletrônico para registro de manifestações, preferencialmente hospedado na Plataforma Fala.BR;\n\n"
        "Art. 7º, § 5º Enquanto não houver adesão à Plataforma Fala.BR, as manifestações deverão ser registradas em sistema próprio ou em planilha controlada, asseguradas a atribuição de número de protocolo, a rastreabilidade e a confidencialidade das informações."
    ),
    "07_Maturidade:M0-08": (
        "Art. 6º, § 2º O ato normativo poderá, quando possível, dispor sobre o mandato do Ouvidor, as condições de substituição "
        "e as regras de confidencialidade aplicáveis às informações tratadas pela unidade.\n\n"
        "Art. 8º, § 2º O ato normativo de criação da Ouvidoria deverá, quando possível, prever mandato fixo para o Ouvidor, "
        "observadas as normas do respectivo ente federativo."
    ),
    "07_Maturidade:M3-60": (
        "Art. 9º A Ouvidoria contará com equipe técnica própria, composta por servidores, preferencialmente com dedicação exclusiva, "
        "destinada a assegurar a adequada análise, o tratamento e o encaminhamento das manifestações."
    ),
    "07_Maturidade:M3-58": (
        "Art. 8º, § 1º O Ouvidor deverá possuir, preferencialmente, formação superior, conhecimento técnico em gestão pública, "
        "controle social, direitos humanos e sistema penal e experiência em escuta qualificada e participação social, observada, "
        "sempre que possível, a escolha dentre os quadros das administrações penais ou da Polícia Penal."
    ),
    "07_Maturidade:M2-50": (
        "Art. 4º A criação e a estruturação das Ouvidorias de Serviços Penais observarão, no mínimo, os seguintes parâmetros:\n"
        "III - acessibilidade e atendimento humanizado, com a disponibilização de canais adequados aos servidores, ao usuário (...);\n"
        "V - integração tecnológica (...).\n\n"
        "Art. 7º, § 2º A Ouvidoria de Serviços Penais deverá disponibilizar canais institucionais de comunicação (...).\n"
        "(Nota: O WhatsApp ou mensagens instantâneas configuram canal de atendimento adicional voltado à ampliação da acessibilidade e humanização do atendimento)."
    ),
    "07_Maturidade:M2-49": (
        "Art. 4º A criação e a estruturação das Ouvidorias de Serviços Penais observarão, no mínimo, os seguintes parâmetros:\n"
        "III - acessibilidade e atendimento humanizado, com a disponibilização de canais adequados aos servidores, ao usuário (...);\n"
        "V - integração tecnológica (...).\n\n"
        "Art. 7º, § 2º A Ouvidoria de Serviços Penais deverá disponibilizar canais institucionais de comunicação, assegurando amplo acesso da sociedade (...)."
    ),
    "07_Maturidade:M2-36": (
        "Art. 7º, § 6º Para apoio às atividades da Ouvidoria de Serviços Penais, recomenda-se que o ente federativo disponibilize recursos administrativos e operacionais, tais como:\n"
        "III - instrumentos de divulgação institucional, compreendendo, no mínimo:\n"
        "a) placas de sinalização;\n"
        "b) cartazes informativos;\n"
        "c) cartões com os contatos da Ouvidoria; e\n"
        "d) materiais informativos de caráter educativo."
    ),
}


def get_fundamentacao_teor_html(occurrence_key: str) -> str:
    """Retorna o teor do dispositivo legal formatado em HTML com parágrafos."""
    raw = LEGAL_TEXTS.get(occurrence_key, "")
    if not raw:
        return ""
    paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip()]
    html_parts = []
    for p in paragraphs:
        lines = [line.strip() for line in p.split("\n") if line.strip()]
        html_parts.append("<p>" + "<br>".join(lines) + "</p>")
    return "".join(html_parts)


def get_fundamentacao_teor_plain(occurrence_key: str) -> str:
    """Retorna o teor do dispositivo legal em texto plano."""
    return LEGAL_TEXTS.get(occurrence_key, "")
