"""
Propósito: Dividir questões por padrão de faixa cinza.
Autor: Alexandre Nassar de Peder
"""

from PIL import Image
import os

Image.MAX_IMAGE_PIXELS = None

def encontrar_faixa_cinza(
    imagem, 
    cor_alvo=(87, 86, 87), 
    tolerancia_cor=25,
    altura_base=29,
    margem_altura=5,      # Aceita faixas de 24px a 34px
    busca_borda_x=40,     # Procura nos últimos 40px da direita
    largura_minima=3      # Exige no mínimo 3px de largura da faixa
):
    imagem = imagem.convert("RGB")
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    altura_min = altura_base - margem_altura  # 24px
    altura_max = altura_base + margem_altura  # 34px
    
    def cor_combina(p):
        return all(abs(c - a) <= tolerancia_cor for c, a in zip(p[:3], cor_alvo))
    
    y = 0
    while y <= altura - altura_min:
        faixa_achada = False
        
        # Varia x do canto direito até 40px para dentro
        for offset_x in range(1, busca_borda_x + 1):
            x = largura - offset_x
            
            if cor_combina(pixels[x, y]):
                # Garante que o pixel acima NÃO é cinza (início da faixa)
                if y > 0 and cor_combina(pixels[x, y - 1]):
                    continue
                
                # Mede altura
                h = 0
                while (y + h < altura) and cor_combina(pixels[x, y + h]):
                    h += 1
                    if h > altura_max:
                        break
                
                # Valida altura
                if altura_min <= h <= altura_max:
                    # Mede largura no meio da faixa para descartar ruído isolado
                    y_meio = y + (h // 2)
                    w = 0
                    while (x - w >= 0) and cor_combina(pixels[x - w, y_meio]):
                        w += 1
                    
                    if w >= largura_minima:
                        posicao_corte = max(0, y - 1) # 1px acima
                        posicoes_corte.append((posicao_corte, h))
                        print(f"Faixa de questão detectada em y={y} (X={x}, Altura={h}px, Largura={w}px). Cortando em y={posicao_corte}")
                        
                        y += h + 5 # Pula a faixa
                        faixa_achada = True
                        break
        
        if not faixa_achada:
            y += 1
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo=(87, 86, 87)):
    if not os.path.exists(caminho_imagem):
        print(f"Erro: Arquivo '{caminho_imagem}' não encontrado.")
        return

    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    print("Processando cortes...")
    
    deteccoes = encontrar_faixa_cinza(imagem, cor_alvo)
    
    if not deteccoes:
        print("\nNenhuma faixa encontrada. Execute o diagnostico.py para checar a cor/posição real.")
        return
    
    print(f"\nTotal de faixas encontradas: {len(deteccoes)}. Cortando...")
    
    os.makedirs(pasta_saida, exist_ok=True)
    posicao_anterior = 0
    
    for i, (posicao_corte, altura_faixa) in enumerate(deteccoes):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte + 1 + altura_faixa
    
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(deteccoes)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"
    pasta_saida = "questoes_divididas"
    cor_do_padrao = (87, 86, 87)
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    print("\nDivisão concluída!")