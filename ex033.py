import sqlite3
import hashlib
import os
import re
from getpass import getpass
from typing import Optional

DB_NAME = "banco.db"


class BancoError(Exception):
    pass


def validar_email(email: str) -> bool:
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(padrao, email))


def gerar_hash_senha(senha: str, salt: Optional[str] = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16).hex()

    senha_hash = hashlib.sha256(
        (senha + salt).encode()
    ).hexdigest()

    return senha_hash, salt


class Banco:
    def __init__(self, db_name: str = DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.criar_tabelas()

    def criar_tabelas(self) -> None:
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            salt TEXT NOT NULL,
            saldo REAL DEFAULT 0 CHECK(saldo >= 0)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            descricao TEXT NOT NULL,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    def cadastrar(self, email: str, senha: str) -> None:
        if not validar_email(email):
            raise BancoError("Email inválido.")

        if len(senha) < 6:
            raise BancoError("A senha deve ter pelo menos 6 caracteres.")

        senha_hash, salt = gerar_hash_senha(senha)

        try:
            self.conn.execute("""
            INSERT INTO usuarios(email, senha, salt)
            VALUES (?, ?, ?)
            """, (email, senha_hash, salt))

            self.conn.commit()

            print("✅ Cadastro realizado com sucesso.")

        except sqlite3.IntegrityError:
            raise BancoError("Este email já está cadastrado.")

    def login(self, email: str, senha: str) -> bool:
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT senha, salt
        FROM usuarios
        WHERE email = ?
        """, (email,))

        usuario = cursor.fetchone()

        if not usuario:
            raise BancoError("Usuário não encontrado.")

        senha_hash, salt = usuario

        tentativa_hash, _ = gerar_hash_senha(senha, salt)

        if tentativa_hash != senha_hash:
            raise BancoError("Senha incorreta.")

        return True

    def obter_saldo(self, email: str) -> float:
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT saldo
        FROM usuarios
        WHERE email = ?
        """, (email,))

        resultado = cursor.fetchone()

        if not resultado:
            raise BancoError("Usuário não encontrado.")

        return resultado[0]

    def atualizar_saldo(self, email: str, valor: float) -> None:
        self.conn.execute("""
        UPDATE usuarios
        SET saldo = saldo + ?
        WHERE email = ?
        """, (valor, email))

    def adicionar_historico(self, email: str, descricao: str) -> None:
        self.conn.execute("""
        INSERT INTO historico(email, descricao)
        VALUES (?, ?)
        """, (email, descricao))

    def depositar(self, email: str, valor: float) -> None:
        if valor <= 0:
            raise BancoError("Valor inválido.")

        self.atualizar_saldo(email, valor)

        self.adicionar_historico(
            email,
            f"Depósito de R$ {valor:.2f}"
        )

        self.conn.commit()

        print("✅ Depósito realizado.")

    def sacar(self, email: str, valor: float) -> None:
        saldo = self.obter_saldo(email)

        if valor <= 0:
            raise BancoError("Valor inválido.")

        if saldo < valor:
            raise BancoError("Saldo insuficiente.")

        self.atualizar_saldo(email, -valor)

        self.adicionar_historico(
            email,
            f"Saque de R$ {valor:.2f}"
        )

        self.conn.commit()

        print("✅ Saque realizado.")

    def transferir(
        self,
        origem: str,
        destino: str,
        valor: float
    ) -> None:

        if valor <= 0:
            raise BancoError("Valor inválido.")

        saldo_origem = self.obter_saldo(origem)

        if saldo_origem < valor:
            raise BancoError("Saldo insuficiente.")

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT email
        FROM usuarios
        WHERE email = ?
        """, (destino,))

        if not cursor.fetchone():
            raise BancoError("Usuário destino não encontrado.")

        try:
            self.conn.execute("BEGIN")

            self.atualizar_saldo(origem, -valor)
            self.atualizar_saldo(destino, valor)

            self.adicionar_historico(
                origem,
                f"Transferência enviada: R$ {valor:.2f} para {destino}"
            )

            self.adicionar_historico(
                destino,
                f"Transferência recebida: R$ {valor:.2f} de {origem}"
            )

            self.conn.commit()

            print("✅ Transferência realizada.")

        except Exception:
            self.conn.rollback()
            raise BancoError("Erro na transferência.")

    def mostrar_historico(self, email: str) -> None:
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT descricao, data
        FROM historico
        WHERE email = ?
        ORDER BY data DESC
        """, (email,))

        dados = cursor.fetchall()

        print("\n📜 Histórico:")
        print("-" * 40)

        for descricao, data in dados:
            print(f"[{data}] {descricao}")

    def fechar(self) -> None:
        self.conn.close()


def menu():
    banco = Banco()

    while True:
        print("\n===== BANCO PYTHON =====")
        print("1 - Cadastrar")
        print("2 - Login")
        print("3 - Sair")

        op = input("Escolha: ")

        try:
            if op == "1":
                email = input("Email: ")
                senha = getpass("Senha: ")

                banco.cadastrar(email, senha)

            elif op == "2":
                email = input("Email: ")
                senha = getpass("Senha: ")

                banco.login(email, senha)

                while True:
                    print("\n===== MENU =====")
                    print("1 - Saldo")
                    print("2 - Depositar")
                    print("3 - Sacar")
                    print("4 - Transferir")
                    print("5 - Histórico")
                    print("6 - Logout")

                    escolha = input("Escolha: ")

                    if escolha == "1":
                        saldo = banco.obter_saldo(email)
                        print(f"💰 Saldo: R$ {saldo:.2f}")

                    elif escolha == "2":
                        valor = float(input("Valor: "))
                        banco.depositar(email, valor)

                    elif escolha == "3":
                        valor = float(input("Valor: "))
                        banco.sacar(email, valor)

                    elif escolha == "4":
                        destino = input("Destino: ")
                        valor = float(input("Valor: "))

                        banco.transferir(email, destino, valor)

                    elif escolha == "5":
                        banco.mostrar_historico(email)

                    elif escolha == "6":
                        break

            elif op == "3":
                banco.fechar()
                print("Encerrando sistema...")
                break

        except BancoError as e:
            print(f"❌ {e}")

        except ValueError:
            print("❌ Digite um valor numérico válido.")


if __name__ == "__main__":
    menu()