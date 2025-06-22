// update_modal.js - JavaScript para o modal de atualização de relatórios

console.log('🚀 update_modal.js carregado');

// Função global para inicializar o modal
window.initUpdateModal = function() {
    console.log('=== INICIALIZANDO MODAL DE ATUALIZAÇÃO ===');
    
    // Aguardar um pouco para garantir que o DOM foi inserido
    setTimeout(function() {
        // Buscar elementos
        const progressRange = document.getElementById('id_progresso_novo');
        const progressValue = document.getElementById('progressValue');
        const statusPreview = document.getElementById('statusPreview');
        const newStatusBadge = document.getElementById('newStatusBadge');
        const saveBtn = document.getElementById('saveUpdateBtn');
        const form = document.getElementById('updateForm');
        
        console.log('🔍 Buscando elementos...');
        console.log('- Slider (id_progresso_novo):', progressRange);
        console.log('- Badge (progressValue):', progressValue);
        console.log('- Preview (statusPreview):', statusPreview);
        console.log('- Badge Status (newStatusBadge):', newStatusBadge);
        console.log('- Botão Salvar (saveUpdateBtn):', saveBtn);
        console.log('- Formulário (updateForm):', form);
        
        // Configurar slider de progresso
        if (progressRange && progressValue) {
            console.log('✅ Configurando slider...');
            console.log('📊 Valor inicial do slider:', progressRange.value);
            
            // Definir valor inicial no badge
            progressValue.textContent = progressRange.value + '%';
            
            // Função para atualizar progresso
            function updateProgress() {
                const value = parseInt(progressRange.value);
                console.log('🎯 SLIDER ALTERADO PARA:', value + '%');
                
                // Atualizar badge imediatamente
                progressValue.textContent = value + '%';
                progressValue.style.backgroundColor = '#0d6efd';
                progressValue.style.color = 'white';
                progressValue.style.fontWeight = 'bold';
                
                // Determinar novo status
                let statusText = '';
                let statusClass = '';
                
                if (value >= 100) {
                    statusText = 'Resolvido';
                    statusClass = 'bg-success';
                } else if (value > 0) {
                    statusText = 'Em Andamento';
                    statusClass = 'bg-warning';
                } else {
                    statusText = 'Pendente';
                    statusClass = 'bg-secondary';
                }
                
                // Atualizar preview do status
                if (newStatusBadge && statusPreview) {
                    newStatusBadge.textContent = statusText;
                    newStatusBadge.className = 'badge fs-6 ' + statusClass;
                    statusPreview.style.display = 'block';
                    console.log('📊 Status preview atualizado para:', statusText);
                }
            }
            
            // TODOS os eventos possíveis para garantir funcionamento
            progressRange.oninput = updateProgress;
            progressRange.onchange = updateProgress;
            progressRange.onmousemove = updateProgress;
            progressRange.addEventListener('input', updateProgress, false);
            progressRange.addEventListener('change', updateProgress, false);
            progressRange.addEventListener('mousemove', updateProgress, false);
            progressRange.addEventListener('touchmove', updateProgress, false);
            
            console.log('✅ Eventos do slider configurados');
            
            // Inicializar imediatamente
            updateProgress();
            
            // Forçar verificação periódica
            const checkInterval = setInterval(function() {
                const currentValue = progressRange.value;
                const displayedValue = progressValue.textContent.replace('%', '');
                
                if (currentValue !== displayedValue) {
                    console.log('🔄 Forçando atualização:', currentValue + '%');
                    updateProgress();
                }
            }, 200);
            
            // Parar verificação após 1 minuto
            setTimeout(() => {
                clearInterval(checkInterval);
                console.log('⏹️ Verificação periódica parada');
            }, 60000);
            
        } else {
            console.error('❌ Slider ou badge não encontrados!');
            console.log('DOM atual:', document.getElementById('updateModal')?.innerHTML);
        }
        
        // Configurar botão salvar
        if (saveBtn && form) {
            console.log('✅ Configurando botão salvar...');
            
            // Remover listeners anteriores
            const newSaveBtn = saveBtn.cloneNode(true);
            saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
            
            newSaveBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log('🔘 BOTÃO SALVAR CLICADO!');
                
                // Validar descrição
                const descricao = form.querySelector('#id_descricao_atualizacao');
                if (!descricao || !descricao.value.trim()) {
                    alert('A descrição da atualização é obrigatória.');
                    console.log('❌ Validação falhou: descrição vazia');
                    return;
                }
                
                console.log('✅ Validação passou');
                
                // Preparar dados
                const formData = new FormData(form);
                const actionUrl = form.getAttribute('action');
                
                console.log('📤 Enviando para URL:', actionUrl);
                console.log('📤 Progresso:', formData.get('progresso_novo'));
                console.log('📤 Descrição:', formData.get('descricao_atualizacao'));
                
                // Mostrar loading
                newSaveBtn.disabled = true;
                newSaveBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Salvando...';
                
                // Enviar requisição
                fetch(actionUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    console.log('📥 Resposta recebida - Status:', response.status);
                    if (!response.ok) {
                        throw new Error('Erro HTTP: ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('📥 Dados da resposta:', data);
                    
                    if (data.success) {
                        console.log('✅ Sucesso! Fechando modal...');
                        
                        // Fechar modal
                        const modal = bootstrap.Modal.getInstance(document.getElementById('updateModal'));
                        if (modal) {
                            modal.hide();
                        }
                        
                        // Mostrar mensagem de sucesso
                        alert('Relatório atualizado com sucesso!');
                        
                        // Recarregar página
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    } else {
                        console.log('❌ Erro do servidor:', data.message);
                        alert('Erro: ' + (data.message || 'Erro ao salvar atualização'));
                    }
                })
                .catch(error => {
                    console.error('❌ Erro na requisição:', error);
                    alert('Erro ao processar solicitação: ' + error.message);
                })
                .finally(() => {
                    // Restaurar botão
                    newSaveBtn.disabled = false;
                    newSaveBtn.innerHTML = '<i class="bi bi-check-circle"></i> Salvar Atualização';
                    console.log('🔄 Botão restaurado');
                });
            });
            
            console.log('✅ Botão salvar configurado');
        } else {
            console.error('❌ Botão salvar ou formulário não encontrados!');
        }
        
        console.log('=== MODAL INICIALIZADO COM SUCESSO ===');
        
    }, 500); // Aguardar 500ms
}; 