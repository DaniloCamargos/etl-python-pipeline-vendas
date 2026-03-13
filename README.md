# ADSIM - Sistema de Integração de Dados

<img width="1110" height="757" alt="image" src="https://github.com/user-attachments/assets/3a26a171-e873-4df9-a41d-339859fe6754" />

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

Sistema modular de integração e processamento de dados para gerenciamento de entidades, produtos, deals e atividades comerciais.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Módulos](#módulos)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

## 🎯 Sobre o Projeto

O ADSIM é um sistema de integração desenvolvido para automatizar a extração, transformação e carga (ETL) de dados de múltiplas fontes, com foco em:

- **Gestão de Produtos**: Programação digital, itens comerciais, tabelas de preços
- **Gestão de Deals**: Negociações, propostas e vencimentos
- **Gestão de Entidades**: Organizações e relacionamentos
- **Gestão de Atividades**: Portfolios de clientes e interações
- **Gestão de Usuários**: Controle de acesso e permissões

## 📁 Estrutura do Projeto
```
ADSIM/
├── activity/                 # Módulo de atividades
│   ├── main.py
│   └── requirements.txt
├── configs/                  # Arquivos de configuração
│   ├── .env                 
│   ├── .gitignore
│   └── requirements.txt
├── customerPortfolios/      # Portfolios de clientes
│   ├── main.py
│   └── requirements.txt
├── deals/                   # Módulo de negociações
│   ├── main.py
│   └── requirements.txt
├── deals_dues/              # Vencimentos de deals
│   ├── main.py
│   └── requirements.txt
├── deals_proposals/         # Propostas comerciais
│   ├── main.py
│   └── requirements.txt
├── entities/                # Entidades do sistema
│   ├── main.py
│   └── requirements.txt
├── entities_organization/   # Organizações
│   ├── main.py
│   └── requirements.txt
├── products/                # Módulo de produtos
│   ├── Product/
│   ├── Product_DigitalProgrammingItems_Channel/
│   ├── Product_DigitalProgrammingItems_Device/
│   ├── Product_DigitalProgrammingItems_GeneralProduct/
│   ├── Product_DigitalProgrammingItems_Page/
│   ├── Product_DigitalProgrammingItems_Visibility/
│   ├── ProductDigitalProgramming/
│   ├── ProductDigitalProgrammingItems/
│   ├── ProductDigitalProgrammingItems_CommercialFormat/
│   ├── ProductDigitalProgrammingItems_CostMethod/
│   ├── ProductDigitalProgrammingItems_DisplayLocation/
│   ├── ProductDigitalProgrammingItems_PriceList/
│   ├── ProductDigitalProgrammingItems_Site/
│   ├── ProductProgramming/
│   ├── ProductProgrammingItems/
│   ├── ProductProgrammingItems_Channel/
│   ├── ProductProgrammingItems_CommercialFormat/
│   ├── ProductProgrammingItems_DisplayLocation/
│   ├── ProductProgrammingItems_PriceList/
│   └── ProductProgrammingItems_Program/
├── teste/                   # Ambiente de testes
│   ├── .env
│   └── main.ipynb
└── users/                   # Gestão de usuários
    ├── .gitcloudignore
    ├── .gitmodules
    ├── main.py
    └── requirements.txt
```

## 🚀 Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **Requests**: Cliente HTTP para APIs
- **Python-dotenv**: Gerenciamento de variáveis de ambiente
- **Pandas** *(opcional)*: Manipulação de dados
- **Jupyter Notebook**: Ambiente de testes e desenvolvimento

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Acesso às APIs configuradas
- Credenciais de autenticação

## 🔧 Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/adsim.git
cd adsim
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
```

3. **Ative o ambiente virtual**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Instale as dependências**
```bash
# Instalar dependências globais
pip install -r configs/requirements.txt

# Instalar dependências de cada módulo conforme necessário
pip install -r activity/requirements.txt
pip install -r deals/requirements.txt
# ... e assim por diante
```

## ⚙️ Configuração

1. **Configure as variáveis de ambiente**

Copie o arquivo `.env.example` para `.env` no diretório `configs/`:
```bash
cp configs/.env.example configs/.env
```

2. **Edite o arquivo `.env` com suas credenciais**
```env
# API Configuration
url=https://api.exemplo.com/endpoint
Authorization=Bearer seu_token_aqui

# Database (se aplicável)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=adsim
DB_USER=usuario
DB_PASSWORD=senha

# Environment
ENVIRONMENT=development
DEBUG=True
```

## 💻 Uso

### Executar um módulo específico
```bash
# Exemplo: Módulo de produtos
cd products/Product
python main.py

# Exemplo: Módulo de deals
cd deals
python main.py
```

### Executar todos os módulos
```bash
# Criar script de execução (run_all.py na raiz)
python run_all.py
```

### Exemplo de uso em código
```python
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('configs/.env')

def extract_data():
    url = os.getenv("url")
    headers = {
        "accept": "application/json",
        "Authorization": os.getenv("Authorization")
    }
    
    body = {
        "tabelaPreco": {
            "somenteTabelaVigente": "S",
            "somenteTabelasAtivas": "S"
        }
    }
    
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    
    return response.json()

if __name__ == "__main__":
    data = extract_data()
    print(data)
```

## 📦 Módulos

### 🎯 Activity
Gerenciamento de atividades e interações comerciais.

### 👥 Customer Portfolios
Gestão de portfolios de clientes e segmentações.

### 💼 Deals
Controle de negociações e oportunidades de venda.

### 📅 Deals Dues
Gerenciamento de vencimentos e prazos de deals.

### 📋 Deals Proposals
Processamento de propostas comerciais.

### 🏢 Entities
Gestão de entidades do sistema.

### 🏛️ Entities Organization
Gerenciamento de organizações e hierarquias.

### 📦 Products
Sistema completo de produtos incluindo:
- Produtos físicos e digitais
- Programação de mídia
- Formatos comerciais
- Tabelas de preços
- Canais de exibição
- Locais de exibição

### 👤 Users
Controle de usuários e permissões.

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga os passos:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de código

- Siga a PEP 8 para estilo de código Python
- Adicione docstrings em todas as funções
- Mantenha os requirements.txt atualizados
- Escreva mensagens de commit descritivas

## 📝 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## 📧 Contato

Danilo Camargos - dcamargos@grupoparanaiba.com.br

Link do Projeto: [https://github.com/grupo-paranaiba/pipeline_etl_vendas_paranaiba](https://github.com/grupo-paranaiba/pipeline_etl_vendas_paranaiba)

## 🙏 Agradecimentos

* [Requests](https://docs.python-requests.org/)
* [Python-dotenv](https://pypi.org/project/python-dotenv/)
* [Choose an Open Source License](https://choosealicense.com)

---

⭐ **Desenvolvido com dedicação para otimizar processos de integração de dados**
