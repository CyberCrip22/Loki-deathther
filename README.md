# 🐍 LOKI - O Caçador de Redes


**"Seu firewall não é páreo para um deus da travessura."**

LOKI é um toolkit profissional de auditoria de redes e segurança. Com ele, você pode escanear dispositivos, bloquear conexões indesejadas e testar a resiliência da sua própria rede. E sim, o nome combina perfeitamente.

---

## AVISO LEGAL - LEIA ANTES DE USAR

**ESTE SOFTWARE É FORNECIDO EXCLUSIVAMENTE PARA PROPÓSITOS EDUCACIONAIS E AUDITORIA AUTORIZADA.**

| ✅ Você PODE | ❌ Você NÃO PODE |
|-------------|------------------|
| Testar sua PRÓPRIA rede | Invadir redes sem permissão |
| Aprender sobre segurança | Causar danos a terceiros |
| Auditar redes que você administra | Usar para atividades ilegais |
| Bloquear seus próprios dispositivos | Vender o software sem autorização |

**O AUTOR NÃO SE RESPONSABILIZA POR QUALQUER USO INDEVIDO DESTA FERRAMENTA.**
**VOCÊ É O ÚNICO RESPONSÁVEL PELAS SUAS AÇÕES.**

---

## Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| **Scanner de Rede** | Descobre TODOS os dispositivos na sua rede local (IP, MAC, hostname) |
| **Firewall Controller** | Bloqueia/desbloqueia dispositivos específicos com 1 clique |
| **Modo Apocalipse**     | Derruba toda a internet do seu computador (teste de stress) |
| **Port Scanner**        | Escaneia portas abertas em qualquer dispositivo |
| **Modo Stealth**        | Esconde a janela para operação discreta |
| **Interface Dark Mode** | Tema roxo/cinza inspirado no deus da travessura |
| **Log Completo**        | Todas as ações ficam registradas com timestamp |
| **Executável Portátil** | Um único .exe, não precisa instalar nada |

---

## 🚀 Como Executar

### Opção 1: Executável (.exe) - Recomendado

```bash
1. Baixe o LOKI.exe da seção Releases
2. Clique com botão direito → "Executar como administrador"
3. Pronto! O toolkit está pronto para uso

Opção 2: Rodar com Python
bash

Clone o repositório
git clone https://github.com/catarina/loki.git

Entre na pasta
cd loki

Execute
python loki.py

Opção 3: Compilar seu próprio .exe
bash

pip install pyinstaller
pyinstaller --onefile --windowed --name "LOKI" loki.py

Requisitos

    Windows 10 ou 11 (usa API do Firewall)

    Python 3.8+ (apenas para rodar o código fonte)

    Permissões de Administrador (para todas as funcionalidades)

loki/
├── LOKI.exe          # Executável (Windows)
├── loki.py           # Código fonte principal
├── README.md         # Documentação
├── LICENSE           # MIT License
└── loki.ico          # Ícone personalizado (opcional)

⚖️ ISENÇÃO DE RESPONSABILIDADE

O LOKI é uma ferramenta de AUDITORIA e APRENDIZADO. A autora não se responsabiliza por:

    Uso não autorizado da ferramenta
    Danos causados por uso indevido
    Conteúdos acessados durante os testes
    Problemas de rede causados pelo usuário

Você é o único responsável pelo que faz com esta ferramenta. Use com responsabilidade e ética.
"Com grandes poderes vêm grandes responsabilidades." - Tio Ben

Use com sabedoria. E divirta-se. 🐍

 Contribuindo

Contribuições são bem-vindas! Para contribuir:

    Faça um Fork do projeto
    Crie uma branch (git checkout -b feature/nova-feature)
    Commit suas mudanças (git commit -m 'Adiciona nova feature')
    Push para a branch (git push origin feature/nova-feature)
    Abra um Pull Reques

  O projeto ainda está em modo de desenvolvimento então pode não se adaptar a sua rede ou não funcionar direito por ser uma versão de testes

