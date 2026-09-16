from PIL import Image
import os
import shutil

def cor_proxima(pixel, cor_alvo, tolerancia=5):
    """Verifica se um pixel está dentro da margem de erro da cor alvo."""
    r, g, b = pixel[:3]
    return (abs(r - cor_alvo[0]) <= tolerancia and
            abs(g - cor_alvo[1]) <= tolerancia and
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_faixa_inferior(imagem, cor_alvo, tolerancia=5):
    """
    Percorre a imagem de cima para baixo procurando por uma linha horizontal completa
    na cor especificada (RGB 35, 31, 32).
    Retorna a posição Y onde deve ser feito o corte (1 pixel acima da linha).
    """
    largura, altura = imagem.size
    pixels = imagem.load()

    # Percorre a imagem de cima para baixo
    for y in range(altura):
        # Verifica se todos os pixels da linha y possuem a cor alvo
        linha_completa = True
        for x in range(largura):
            if not cor_proxima(pixels[x, y], cor_alvo, tolerancia):
                linha_completa = False
                break
        
        # Se encontrou a linha inteira da cor desejada
        if linha_completa:
            posicao_corte = max(0, y - 1)  # Corta 1 pixel acima do início do padrão
            print(f"Linha encontrada em y={y}! Cortando na posição y={posicao_corte}")
            return posicao_corte

    return None

def processar_imagens(pasta_origem, pasta_destino, cor_alvo):
    """
    Processa todas as imagens da pasta origem, recortando as que têm a linha especificada
    e copiando todas para a pasta destino.
    """
    os.makedirs(pasta_destino, exist_ok=True)

    arquivos = [f for f in os.listdir(pasta_origem) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]

    print(f"Encontrados {len(arquivos)} arquivos para processar")

    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)

        try:
            with Image.open(caminho_origem) as imagem:
                print(f"\nProcessando: {arquivo} ({imagem.width}x{imagem.height})")

                posicao_corte = encontrar_faixa_inferior(imagem, cor_alvo)

                if posicao_corte is not None and posicao_corte > 0:
                    area_corte = (0, 0, imagem.width, posicao_corte)
                    imagem_recortada = imagem.crop(area_corte)
                    imagem_recortada.save(caminho_destino)
                    print(f"✓ Imagem recortada: {imagem_recortada.width}x{imagem_recortada.height}")
                else:
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"✓ Imagem mantida original (sem linha detectada)")

        except Exception as e:
            print(f"✗ Erro ao processar {arquivo}: {e}")
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print(f"✓ Arquivo copiado mesmo com erro")
            except:
                print(f"✗ Não foi possível copiar o arquivo")

if __name__ == "__main__":
    pasta_origem = "questoes"
    pasta_destino = "finalizadas"
    cor_alvo = (35, 31, 32)  # Cor RGB solicitada (35, 31, 32)

    print("Iniciando processamento de imagens...")
    print(f"Pasta origem: {pasta_origem}")
    print(f"Pasta destino: {pasta_destino}")
    print(f"Cor alvo: RGB{cor_alvo}")

    if not os.path.exists(pasta_origem):
        print(f"Erro: A pasta '{pasta_origem}' não existe!")
        exit(1)

    processar_imagens(pasta_origem, pasta_destino, cor_alvo)

    print("\n" + "="*50)
    print("Processamento concluído!")
    print(f"Todas as imagens foram salvas em: {pasta_destino}")