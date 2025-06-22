from django.core.management.base import BaseCommand
from authentication.models import Perfil, Unidade, Setor


class Command(BaseCommand):
    help = 'Popula dados iniciais da estrutura organizacional'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando população da estrutura organizacional...'))
        
        # Criar Perfis
        perfis_data = [
            {
                'nome': 'Super Admin',
                'descricao': 'Acesso total ao sistema, pode gerenciar todos os módulos e usuários',
                'nivel_acesso': 4
            },
            {
                'nome': 'Admin',
                'descricao': 'Acesso administrativo, pode gerenciar usuários e relatórios',
                'nivel_acesso': 3
            },
            {
                'nome': 'Manager',
                'descricao': 'Acesso de gerenciamento, pode aprovar e atribuir relatórios',
                'nivel_acesso': 2
            },
            {
                'nome': 'Usuário',
                'descricao': 'Acesso básico, pode criar e visualizar relatórios próprios',
                'nivel_acesso': 1
            }
        ]
        
        for perfil_data in perfis_data:
            perfil, created = Perfil.objects.get_or_create(
                nome=perfil_data['nome'],
                defaults=perfil_data
            )
            if created:
                self.stdout.write(f'✅ Perfil criado: {perfil.nome}')
            else:
                self.stdout.write(f'ℹ️ Perfil já existe: {perfil.nome}')
        
        # Criar Unidades
        unidades_data = [
            {
                'codigo': 'PROD',
                'nome': 'Produção',
                'descricao': 'Unidade responsável pela produção e manufatura',
                'responsavel': 'Gerente de Produção'
            },
            {
                'codigo': 'MANUT',
                'nome': 'Manutenção',
                'descricao': 'Unidade responsável pela manutenção de equipamentos',
                'responsavel': 'Supervisor de Manutenção'
            },
            {
                'codigo': 'QUAL',
                'nome': 'Controle de Qualidade',
                'descricao': 'Unidade responsável pelo controle e garantia da qualidade',
                'responsavel': 'Coordenador de Qualidade'
            },
            {
                'codigo': 'ADM',
                'nome': 'Administrativo',
                'descricao': 'Unidade administrativa e de gestão',
                'responsavel': 'Gerente Administrativo'
            },
            {
                'codigo': 'TI',
                'nome': 'Tecnologia da Informação',
                'descricao': 'Unidade de suporte tecnológico e sistemas',
                'responsavel': 'Coordenador de TI'
            }
        ]
        
        for unidade_data in unidades_data:
            unidade, created = Unidade.objects.get_or_create(
                codigo=unidade_data['codigo'],
                defaults=unidade_data
            )
            if created:
                self.stdout.write(f'✅ Unidade criada: {unidade.nome}')
            else:
                self.stdout.write(f'ℹ️ Unidade já existe: {unidade.nome}')
        
        # Criar Setores
        setores_data = [
            {
                'codigo': 'MELET',
                'nome': 'M_ELETRICA',
                'descricao': 'Setor de manutenção elétrica',
                'unidade_codigo': 'MANUT',
                'responsavel': 'Técnico Elétrico Sênior'
            },
            {
                'codigo': 'MMECA',
                'nome': 'M_MECANICA',
                'descricao': 'Setor de manutenção mecânica',
                'unidade_codigo': 'MANUT',
                'responsavel': 'Técnico Mecânico Sênior'
            },
            {
                'codigo': 'REFRI',
                'nome': 'REFRIGERACAO',
                'descricao': 'Setor de refrigeração e climatização',
                'unidade_codigo': 'MANUT',
                'responsavel': 'Técnico em Refrigeração'
            },
            {
                'codigo': 'PROD',
                'nome': 'PRODUCAO',
                'descricao': 'Setor de produção e operação',
                'unidade_codigo': 'PROD',
                'responsavel': 'Supervisor de Produção'
            },
            {
                'codigo': 'CQUAL',
                'nome': 'C_QUALIDADE',
                'descricao': 'Setor de controle de qualidade',
                'unidade_codigo': 'QUAL',
                'responsavel': 'Analista de Qualidade'
            },
            {
                'codigo': 'TERC',
                'nome': 'TERCEIRO',
                'descricao': 'Setor para empresas terceirizadas',
                'unidade_codigo': 'ADM',
                'responsavel': 'Coordenador de Terceiros'
            }
        ]
        
        for setor_data in setores_data:
            # Buscar a unidade
            try:
                unidade = Unidade.objects.get(codigo=setor_data['unidade_codigo'])
            except Unidade.DoesNotExist:
                unidade = None
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Unidade {setor_data["unidade_codigo"]} não encontrada para setor {setor_data["codigo"]}')
                )
            
            setor_create_data = {
                'codigo': setor_data['codigo'],
                'nome': setor_data['nome'],
                'descricao': setor_data['descricao'],
                'responsavel': setor_data['responsavel'],
                'unidade': unidade
            }
            
            setor, created = Setor.objects.get_or_create(
                codigo=setor_data['codigo'],
                defaults=setor_create_data
            )
            if created:
                self.stdout.write(f'✅ Setor criado: {setor.get_nome_display()}')
            else:
                self.stdout.write(f'ℹ️ Setor já existe: {setor.get_nome_display()}')
        
        # Estatísticas finais
        total_perfis = Perfil.objects.count()
        total_unidades = Unidade.objects.count()
        total_setores = Setor.objects.count()
        
        self.stdout.write(self.style.SUCCESS('\n📊 Estrutura organizacional populada com sucesso!'))
        self.stdout.write(f'   • {total_perfis} perfis cadastrados')
        self.stdout.write(f'   • {total_unidades} unidades cadastradas')
        self.stdout.write(f'   • {total_setores} setores cadastrados')
        
        self.stdout.write(self.style.SUCCESS('\n🔗 Acesse /auth/estrutura/ para visualizar a estrutura completa')) 