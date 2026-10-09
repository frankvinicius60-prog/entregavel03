"""Demonstração do meu projeto de Programação Orientada a Objetos."""
from modelos import Banco, Cliente, ContaCorrente, ContaPoupanca
from modelos import SaldoInsuficienteError


def main():
    """Cria dez contas e demonstra operações, polimorfismo e erros."""
    banco = Banco('Banco Acadêmico')
    for indice in range(1, 11):
        cliente = Cliente(f'Cliente {indice}', f'cliente{indice}@example.com')
        if indice % 2:
            conta = ContaCorrente(str(1000 + indice), cliente, saldo=1000)
        else:
            conta = ContaPoupanca(str(1000 + indice), cliente, saldo=1000)
        banco.adicionar_conta(conta)

    print(f'{banco}\n')
    for conta in banco.contas:
        # Mesma chamada, com comportamentos distintos nas classes filhas.
        print(conta.processar_mes())
        print(conta)
    conta = banco.contas[0]
    conta.depositar(50)
    conta.sacar(20)
    print(f'\nApós depósito e saque: {conta}')
    print(f'Representação para depuração: {conta!r}')
    print('\nDemonstração de entradas inválidas:')
    for valor in [-10, 'abc', 'NaN']:
        try:
            conta.depositar(valor)
        except ValueError as erro:
            print(f'Depósito {valor!r} rejeitado: {erro}')
    try:
        conta.sacar(999999)
    except SaldoInsuficienteError as erro:
        print(f'Saque rejeitado: {erro}')
    try:
        conta.titular.email = 'email-sem-arroba'
    except ValueError as erro:
        print(f'Alteração de e-mail rejeitada: {erro}')
    try:
        conta.saldo = -1
    except ValueError as erro:
        print(f'Alteração de saldo rejeitada: {erro}')
    print(f'\nEstado preservado: {conta}')


if __name__ == '__main__':
    main()
