from PIL import Image
import os

def cor_proxima(pixel_cor, cor_alvo, tolerancia=3):
    """
    Verifica se uma cor RGB/RGBA está dentro da margem de erro da cor alvo.
    """
    r, g, b = pixel_cor[:3]
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_padrao_vertical(imagem, x_coluna=325):
    """
    Percorre a coluna x_coluna de cima para baixo procurando pelo padrão vertical:
    - 1 px RGB (255, 255, 255)
    - 30 px (margem de 27 a 33 px) RGB (222, 221, 222)
    - 1 px RGB (255, 255, 255)
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    COR_BRANCA = (255, 255, 255)
    COR_CINZA = (222, 221, 222)
    
    y = 0
    # Limite considerando a menor faixa possível (1 + 27 + 1 = 29 pixels)
    while y < altura - 29:
        # 1. Verifica se o primeiro pixel do padrão é branco
        if cor_proxima(pixels[x_coluna, y], COR_BRANCA):
            
            # 2. Conta a altura da faixa cinza subsequente
            altura_cinza = 0
            temp_y = y + 1
            while temp_y < altura and cor_proxima(pixels[x_coluna, temp_y], COR_CINZA):
                altura_cinza += 1
                temp_y += 1
            
            # 3. Verifica se a faixa cinza está entre 27 e 33 pixels (30 +/- 3)
            if 27 <= altura_cinza <= 33:
                # 4. Verifica se o pixel logo após a faixa cinza é branco
                if temp_y < altura and cor_proxima(pixels[x_coluna, temp_y], COR_BRANCA):
                    
                    # Corta 7 pixels antes do início do padrão para mantê-los no topo da imagem
                    posicao_corte = max(0, y - 7)
                    
                    posicoes_corte.append(posicao_corte)
                    print(f"Padrão encontrado em y={y} (faixa cinza: {altura_cinza}px). Cortando em y={posicao_corte}")
                    
                    # Pula o padrão encontrado para evitar detecção dupla
                    y = temp_y + 1
                    continue
        y += 1
        
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente com base nas posições do padrão encontrado.
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_padrao_vertical(imagem, x_coluna=325)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} ocorrências do padrão para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
    
    # Corta a seção final após o último corte
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "inteiras_concatenadas_verticalmente.png"  # Atualize para sua imagem
    pasta_saida = "inteiras"                         # Atualize para sua pasta de saída
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    print("Divisão concluída!")