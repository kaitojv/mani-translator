from flask import Flask, request, jsonify
from anthropic import Anthropic
import os

app = Flask(__name__)

# A Vercel pega a sua chave automaticamente das variáveis de ambiente de forma segura
cliente = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route('/api/traduzir', methods=['POST'])
def traduzir():
    dados = request.json
    texto_usuario = dados.get('texto')
    direcao = dados.get('direcao')

    if not texto_usuario:
        return jsonify({"erro": "Nenhum texto enviado"}), 400

    is_pt = (direcao == 'pt-mani')
    
    # Prompt com as regras de tradução e estrutura do Mani
    system_prompt = f"""Você é um tradutor especializado na língua construída Mani.

    CARACTERES ESPECIAIS E ALFABETO:
    • λ = ɐ̃ (ã nasal)
    • ɛ = é
    • ɔ = ó
    • თ = ch/x/sh
    • ṫ = th inglês
    • ჰ = ks
    • რ = rr forte
    • L = l normal (usado no lugar do antigo ŀ)
    • ' = pausa glotal (morfema, não pontuação)

    GRAMÁTICA:
    • A forma principal e mais usada da língua é OVA (Objeto-Verbo-Agente), com o sujeito sempre no final.
    • É permitido também o uso da ordem Sujeito-Verbo-Objeto (SVO) como forma de adaptação ocidental.
    • Verbos terminam em -r.
    • Agente aglutina-se ao verbo: 'ma=eu 'ta=você 'lo=ele 'la=ela 'le=neutro 'li=inanimado 'mas=nós 'tas=vocês 'los=eles 'las=elas
    • Tempo: kin=passado kλn=futuro (ausente=presente) — vêm imediatamente antes do verbo
    • Zero-cópula: adj/subst+'agente. Ex: bɔno'lo=ele é bom; kaliz'ma=eu sou feliz
    • Casos: ir'=acusativo(objeto animado) un'=genitivo(posse) ɛs'=ablativo(origem) vel'=comparativo

    VOCABULÁRIO ESSENCIAL:
    • ser/estar = vimur | ter = pozir | ir = bur | vir = bor
    • sol = kɔro | lua = mila (ou Lukir mila) | céu = sipa | estrela = silεu
    • saber/conhecer = jetɛr
    • animal = lɔmun | pessoa = avita
    • agora/momento presente = namu
    • hoje = tukan | amanhã = pouna | ontem = turmoi
    
    {'Traduza o texto do Português para a língua Mani. Retorne:\n[TRADUÇÃO EM MANI]\n---\n[Nota gramatical breve: slots usados e formas morfológicas, máx. 2 linhas]' if is_pt else 'Traduza o texto da língua Mani para o Português natural e fluente. Retorne:\n[TRADUÇÃO EM PORTUGUÊS]\n---\n[Análise morfológica breve: formas identificadas, máx. 2 linhas]'}
    """

    try:
        # Comunicação com o Claude
        resposta = cliente.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": texto_usuario}]
        )
        
        texto_traduzido = resposta.content[0].text
        return jsonify({"traducao": texto_traduzido})
        
    except Exception as e:
        return jsonify({"erro": f"Falha na comunicação com a IA: {str(e)}"}), 500