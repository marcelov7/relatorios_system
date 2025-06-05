# Sistema de Relatórios Django

Sistema completo de relatórios desenvolvido em Django com funcionalidades de autenticação, dashboard, geração de PDFs, notificações e muito mais.

## 🚀 Funcionalidades

- **Autenticação Completa**: Login, logout, registro e perfil de usuários
- **Sistema de Relatórios**: CRUD completo com categorização
- **Geração de PDFs**: Relatórios em PDF e Excel
- **Dashboard Interativo**: Gráficos e estatísticas
- **Notificações**: Sistema de notificações em tempo real
- **Interface Moderna**: Bootstrap 5 responsivo
- **Deploy no Render**: Configurado para hospedagem na nuvem

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 4.2.7
- **Banco de Dados**: PostgreSQL
- **Frontend**: Bootstrap 5, JavaScript
- **Relatórios**: ReportLab, Pandas
- **Notificações**: django-notifications-hq
- **Deploy**: Render.com
- **Cache/Filas**: Redis, Celery

## 📦 Instalação e Configuração

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd DjangoSistem
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
Copie o arquivo `env.example` para `.env` e configure as variáveis:
```bash
cp env.example .env
```

### 5. Execute as migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crie um superusuário
```bash
python manage.py createsuperuser
```

### 7. Execute o servidor
```bash
python manage.py runserver
```

## 🚀 Deploy no Render

### 1. Configuração do Banco de Dados
- O sistema já está configurado para usar o PostgreSQL do Render
- As credenciais estão no arquivo `render.yaml`

### 2. Variáveis de Ambiente no Render
Configure as seguintes variáveis no painel do Render:
- `SECRET_KEY`: Chave secreta do Django
- `DEBUG`: False para produção
- `DB_NAME`: dbrelatorio_rqkg
- `DB_USER`: dbrelatorio_rqkg_user
- `DB_PASSWORD`: CJZUYC4FeqPg3FfSZDVu75oSaXhpzPwV
- `DB_HOST`: dpg-d10oti95pdvs73acede0-a.oregon-postgres.render.com
- `DB_PORT`: 5432

### 3. Deploy
O deploy será automático após o push para o repositório conectado.

## 📱 Estrutura do Projeto

```
DjangoSistem/
├── relatorio_system/          # Configurações principais do Django
├── core/                      # App principal (home, about)
├── authentication/            # Sistema de autenticação
├── reports/                   # Sistema de relatórios
├── dashboard/                 # Dashboard e analytics
├── notifications_app/         # Sistema de notificações
├── templates/                 # Templates HTML
├── static/                    # Arquivos estáticos (CSS, JS)
├── media/                     # Arquivos de upload
├── requirements.txt           # Dependências Python
├── render.yaml               # Configuração do Render
└── README.md                 # Este arquivo
```

## 🎯 Funcionalidades Detalhadas

### Sistema de Autenticação
- Registro de novos usuários
- Login/logout seguro
- Perfil de usuário com foto
- Diferentes níveis de acesso (usuário comum, gerente, admin)

### Sistema de Relatórios
- Criação de relatórios com categorias
- Editor de dados dos relatórios
- Geração automática de PDFs
- Exportação para Excel
- Controle de visibilidade (público/privado)
- Sistema de views e downloads

### Dashboard
- Estatísticas em tempo real
- Gráficos interativos
- Análise de dados
- Relatórios mais acessados
- Atividade recente

### Notificações
- Notificações em tempo real
- Configurações personalizáveis
- Envio por email
- Histórico de notificações
- APIs para integração

## 🔧 Comandos Úteis

### Desenvolvimento
```bash
# Executar servidor de desenvolvimento
python manage.py runserver

# Fazer migrações
python manage.py makemigrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic

# Executar testes
python manage.py test
```

### Dados de Exemplo
```bash
# Criar categorias de exemplo
python manage.py shell
>>> from reports.models import ReportCategory
>>> ReportCategory.objects.create(name="Vendas", description="Relatórios de vendas", color="#007bff")
>>> ReportCategory.objects.create(name="Financeiro", description="Relatórios financeiros", color="#28a745")
```

## 📞 Suporte

Para dúvidas ou suporte, entre em contato através do GitHub.

## 📄 Licença

Este projeto está sob a licença MIT.

---

Desenvolvido com ❤️ usando Django e Bootstrap 