"""Classes do meu sistema bancário didático, sem conexão com bancos reais."""
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation
import re


def validar_valor(valor, positivo=False):
    """Converte um valor para Decimal e rejeita valores inválidos."""
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        raise ValueError('Informe um valor numérico válido.') from None
    if not numero.is_finite() or numero < 0:
        raise ValueError('O valor deve ser finito e não negativo.')
    if positivo and numero == 0:
        raise ValueError('O valor deve ser maior que zero.')
    try:
        arredondado = numero.quantize(Decimal('0.01'))
    except InvalidOperation:
        raise ValueError('O valor excede a precisão suportada.') from None
    if numero != arredondado:
        raise ValueError('Use no máximo duas casas decimais.')
    return arredondado


class SaldoInsuficienteError(Exception):
    """Indica uma tentativa de saque maior que o saldo disponível."""


class Cliente:
    """Representa o titular de uma conta."""

    def __init__(self, nome, email):
        self.nome = nome
        self.email = email

    @property
    def nome(self):
        """Retorna o nome do cliente."""
        return self._nome

    @nome.setter
    def nome(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError('O nome não pode ficar vazio.')
        self._nome = valor.strip()

    @property
    def email(self):
        """Retorna o e-mail do cliente."""
        return self._email

    @email.setter
    def email(self, valor):
        if not isinstance(valor, str) or not re.fullmatch(
            r'[A-Za-z0-9_.+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}',
            valor.strip(),
        ):
            raise ValueError('E-mail inválido.')
        self._email = valor.strip()

    def __str__(self):
        return f'{self.nome} <{self.email}>'

    def __repr__(self):
        return f'Cliente(nome={self.nome!r}, email={self.email!r})'


class Conta(ABC):
    """Define o contrato comum das contas; não pode ser instanciada."""

    def __init__(self, numero, titular, saldo=0):
        if not isinstance(numero, str) or not numero.strip():
            raise ValueError('O número da conta não pode ficar vazio.')
        self._numero = numero.strip()
        self.titular = titular
        self.saldo = saldo

    @property
    def numero(self):
        """Retorna a identificação imutável da conta."""
        return self._numero

    @property
    def titular(self):
        """Retorna o objeto Cliente associado à conta."""
        return self._titular

    @titular.setter
    def titular(self, valor):
        if not isinstance(valor, Cliente):
            raise ValueError('O titular precisa ser um objeto Cliente.')
        self._titular = valor

    @property
    def saldo(self):
        """Retorna o saldo validado da conta."""
        return self._saldo

    @saldo.setter
    def saldo(self, valor):
        self._saldo = validar_valor(valor)

    def depositar(self, valor):
        """Adiciona um valor positivo ao saldo."""
        self.saldo += validar_valor(valor, positivo=True)

    def sacar(self, valor):
        """Retira um valor positivo sem permitir saldo negativo."""
        valor = validar_valor(valor, positivo=True)
        if valor > self.saldo:
            raise SaldoInsuficienteError('Saldo insuficiente para o saque.')
        self.saldo -= valor

    @abstractmethod
    def processar_mes(self):
        """Aplica a regra mensal específica da modalidade."""

    def __str__(self):
        return (
            f'{type(self).__name__} {self.numero} | '
            f'{self.titular.nome} | Saldo: R$ {self.saldo:.2f}'
        )

    def __repr__(self):
        return (
            f'{type(self).__name__}(numero={self.numero!r}, '
            f'titular={self.titular!r}, saldo={str(self.saldo)!r})'
        )


class ContaCorrente(Conta):
    """Conta que desconta uma tarifa mensal, limitada ao saldo."""

    def __init__(self, numero, titular, saldo=0, tarifa=10):
        super().__init__(numero, titular, saldo)
        self.tarifa = tarifa

    @property
    def tarifa(self):
        """Retorna a tarifa mensal."""
        return self._tarifa

    @tarifa.setter
    def tarifa(self, valor):
        self._tarifa = validar_valor(valor)

    def processar_mes(self):
        """Desconta a tarifa sem deixar a conta negativa."""
        desconto = min(self.tarifa, self.saldo)
        self.saldo -= desconto
        return f'Conta {self.numero}: tarifa descontada de R$ {desconto:.2f}'

    def __str__(self):
        return f'{super().__str__()} | Tarifa: R$ {self.tarifa:.2f}'


class ContaPoupanca(Conta):
    """Conta que adiciona um rendimento mensal ao saldo."""

    def __init__(self, numero, titular, saldo=0, taxa=0.005):
        super().__init__(numero, titular, saldo)
        self.taxa = taxa

    @property
    def taxa(self):
        """Retorna a taxa mensal em formato decimal."""
        return self._taxa

    @taxa.setter
    def taxa(self, valor):
        try:
            taxa = Decimal(str(valor))
        except (InvalidOperation, ValueError):
            raise ValueError('Taxa inválida.') from None
        if not taxa.is_finite() or not 0 <= taxa <= 1:
            raise ValueError('A taxa precisa estar entre 0 e 1.')
        self._taxa = taxa

    def processar_mes(self):
        """Acrescenta rendimento arredondado para centavos."""
        rendimento = (self.saldo * self.taxa).quantize(Decimal('0.01'))
        self.saldo += rendimento
        return f'Conta {self.numero}: rendimento de R$ {rendimento:.2f}'

    def __str__(self):
        return f'{super().__str__()} | Taxa: {self.taxa * 100:.2f}%'


class Banco:
    """Agrupa contas e impede números duplicados."""

    def __init__(self, nome):
        self.nome = nome
        self._contas = []

    @property
    def nome(self):
        """Retorna o nome do banco didático."""
        return self._nome

    @nome.setter
    def nome(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError('O banco precisa de um nome.')
        self._nome = valor.strip()

    @property
    def contas(self):
        """Expõe uma tupla para proteger a coleção contra alterações externas."""
        return tuple(self._contas)

    def adicionar_conta(self, conta):
        """Inclui uma conta válida com número ainda não cadastrado."""
        if not isinstance(conta, Conta):
            raise ValueError('Informe um objeto Conta.')
        if any(item.numero == conta.numero for item in self._contas):
            raise ValueError('Número de conta já cadastrado.')
        self._contas.append(conta)

    def __len__(self):
        return len(self._contas)

    def __str__(self):
        return f'{self.nome}: {len(self)} contas cadastradas'

    def __repr__(self):
        return f'Banco(nome={self.nome!r}, quantidade_contas={len(self)})'
