# language: pt
Funcionalidade: Compra de produto na GeekStore
  Como um cliente da GeekStore
  Quero comprar um produto informando meu cartão
  Para que eu receba a confirmação da compra

  Cenário: Compra com sucesso sem cupom
    Dado que o produto "teclado" está disponível no estoque
    Quando eu realizo a compra do produto "teclado" com o cartão "1234-5678" sem cupom
    Então a compra é aprovada com sucesso
    E o valor pago é 200.0

  Cenário: Compra com sucesso usando cupom GEEK20
    Dado que o produto "teclado" está disponível no estoque
    Quando eu realizo a compra do produto "teclado" com o cartão "1234-5678" e o cupom "GEEK20"
    Então a compra é aprovada com sucesso
    E o valor pago é 160.0

  Cenário: Tentativa de compra de produto sem estoque
    Dado que o produto "sem_estoque" não possui estoque
    Quando eu realizo a compra do produto "sem_estoque" com o cartão "1234-5678" sem cupom
    Então a compra é recusada com erro de estoque
