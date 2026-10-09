"""Testes das regras e da preservação do estado dos objetos."""
import unittest
from decimal import Decimal
from modelos import (
    Banco, Cliente, Conta, ContaCorrente, ContaPoupanca,
    SaldoInsuficienteError,
)


class TestesSistema(unittest.TestCase):
    """Confere os principais comportamentos das classes."""

    def setUp(self):
        self.cliente = Cliente('Ana', 'ana@example.com')
        self.conta = ContaCorrente('1', self.cliente, 100)

    def test_classe_abstrata(self):
        with self.assertRaises(TypeError):
            Conta('1', self.cliente)

    def test_operacoes(self):
        self.conta.depositar('25.50')
        self.conta.sacar(10)
        self.assertEqual(self.conta.saldo, Decimal('115.50'))

    def test_saque_preserva_saldo(self):
        with self.assertRaises(SaldoInsuficienteError):
            self.conta.sacar(101)
        self.assertEqual(self.conta.saldo, Decimal('100.00'))

    def test_valores_invalidos(self):
        for valor in [-1, 'abc', 'NaN', 'Infinity', '1.001', 0]:
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    self.conta.depositar(valor)
                self.assertEqual(self.conta.saldo, Decimal('100.00'))

    def test_setters_preservam_estado(self):
        with self.assertRaises(ValueError):
            self.conta.saldo = -10
        with self.assertRaises(ValueError):
            self.cliente.email = 'invalido'
        self.assertEqual(self.conta.saldo, Decimal('100.00'))
        self.assertEqual(self.cliente.email, 'ana@example.com')

    def test_polimorfismo(self):
        poupanca = ContaPoupanca('2', self.cliente, 100, taxa='0.01')
        for conta in [self.conta, poupanca]:
            conta.processar_mes()
        self.assertEqual(self.conta.saldo, Decimal('90.00'))
        self.assertEqual(poupanca.saldo, Decimal('101.00'))

    def test_tarifa_limitada_ao_saldo(self):
        conta = ContaCorrente('2', self.cliente, 5, tarifa=10)
        conta.processar_mes()
        self.assertEqual(conta.saldo, Decimal('0.00'))

    def test_banco_e_dez_instancias(self):
        banco = Banco('Teste')
        for indice in range(10):
            classe = ContaCorrente if indice % 2 else ContaPoupanca
            banco.adicionar_conta(classe(str(indice), self.cliente))
        self.assertEqual(len(banco), 10)
        self.assertIsInstance(banco.contas, tuple)
        with self.assertRaises(ValueError):
            banco.adicionar_conta(ContaCorrente('0', self.cliente))
        self.assertEqual(len(banco), 10)

    def test_taxa_invalida(self):
        poupanca = ContaPoupanca('2', self.cliente)
        for taxa in [-1, 2, 'NaN', 'abc']:
            with self.subTest(taxa=taxa):
                with self.assertRaises(ValueError):
                    poupanca.taxa = taxa
        self.assertEqual(poupanca.taxa, Decimal('0.005'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
