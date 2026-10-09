# Canvas do Projeto

Seis diagramas da arquitetura do Cinematica. Abra [`index.html`](index.html) no
navegador para navegar entre eles.

| Artboard | Conteúdo |
| --- | --- |
| [`Main.dc.html`](Main.dc.html) | Visão geral — a ingestão offline e o caminho de uma pergunta |
| [`Pipeline.dc.html`](Pipeline.dc.html) | Os cinco estágios do ETL, suas entradas e saídas |
| [`Agente.dc.html`](Agente.dc.html) | Os cinco estágios do LangGraph, o retry e as três saídas do `verify` |
| [`Grafo.dc.html`](Grafo.dc.html) | Os nove rótulos de nó e as relações entre eles |
| [`Tools.dc.html`](Tools.dc.html) | As oito grounding tools, entre leitura e escrita |
| [`Estado.dc.html`](Estado.dc.html) | O que está verificado, o que nunca rodou, o que ficou em aberto |

## Sobre os arquivos

Cada `.dc.html` é um artboard autocontido, com largura fixa de 1600px e todo o
estilo inline. Eles abrem direto no navegador, sem build e sem servidor.

O cabeçalho referencia `./support.js`, que é o runtime do editor de canvas onde
estes arquivos foram criados. Esse arquivo não está aqui e dá 404 — sem efeito
sobre o que é exibido, porque o conteúdo é markup literal, sem placeholders a
interpolar.

`canvas.json` é o índice do editor: guarda o enquadramento de cada artboard na
tela infinita (posição, largura, altura) e os títulos das seções. Ele não é lido
pelos arquivos HTML e só importa se o canvas for reaberto no editor.

## Editando

Os artboards são HTML comum: dá para editar qualquer card ou texto direto no
arquivo. As setas, porém, são posicionadas por coordenadas absolutas calculadas
a partir das caixas que elas ligam — mover ou redimensionar um card exige
recalcular cada seta que o toca.

A versão viva deste canvas, com edição visual, está em
[claude.ai/artifact/VR8zVx2T72oyXJi2tSVHDb](https://claude.ai/artifact/VR8zVx2T72oyXJi2tSVHDb)
— privada, visível apenas para o dono e para quem receber acesso.
