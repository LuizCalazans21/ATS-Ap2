def verifica_lista_produtos(response):
    
    dados = response.json()
    assert isinstance(dados, list), "Resposta deve ser uma lista"
    assert len(dados) > 0, "Lista não pode estar vazia"
    for produto in dados:
        assert "nome" in produto, f"Chave 'nome' ausente em {produto}"
        assert "preco" in produto, f"Chave 'preco' ausente em {produto}"
        assert "estoque" in produto, f"Chave 'estoque' ausente em {produto}"
        assert isinstance(produto["preco"], (int, float)), "Preço deve ser numérico"
        assert isinstance(produto["estoque"], int), "Estoque deve ser inteiro"