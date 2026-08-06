Trabalho — Desenvolvimento de um sistema bancário em Python

Uma instituição financeira deseja desenvolver um sistema bancário simples em Python, utilizando SQLite para persistência dos dados. O sistema deverá permitir o cadastro e autenticação de usuários, gerenciamento de saldo e registro das operações realizadas.

Desenvolva uma aplicação orientada a objetos que atenda aos seguintes requisitos:

1. Crie uma classe responsável pelo gerenciamento do banco de dados utilizando sqlite3.
2. Crie uma tabela usuarios contendo:
    * identificador único;
    * e-mail;
    * senha;
    * salt para proteção da senha;
    * saldo do usuário.
3. Crie uma tabela historico para registrar as operações realizadas pelos usuários, contendo e-mail, descrição e data da operação.
4. Implemente o cadastro de usuários, verificando:
    * se o e-mail possui formato válido;
    * se a senha possui pelo menos 6 caracteres;
    * se o e-mail já está cadastrado.
5. As senhas não devem ser armazenadas em texto puro. Utilize hashlib e um salt aleatório para gerar o hash da senha.
6. Implemente um sistema de login, verificando o e-mail e comparando o hash da senha informada com o hash armazenado.
7. Após o login, permita ao usuário:
    * consultar o saldo;
    * realizar depósitos;
    * realizar saques, impedindo valores maiores que o saldo disponível;
    * realizar transferências entre usuários;
    * consultar o histórico de operações;
    * realizar logout.
8. Todas as operações financeiras devem ser registradas no histórico.
9. Na transferência, utilize transação do banco de dados, garantindo que, caso ocorra algum erro, as alterações sejam desfeitas (rollback).
10. Utilize tratamento de exceções para erros relacionados às regras do sistema e para entradas numéricas inválidas.
11. Utilize consultas parametrizadas para evitar problemas de SQL Injection.
12. Organize o programa de forma modular, utilizando funções, classes, métodos e boas práticas de programação.
