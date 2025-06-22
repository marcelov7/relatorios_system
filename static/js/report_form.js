document.addEventListener('DOMContentLoaded', function() {
    // Atualizar preview do progresso e status automaticamente
    const progressInput = document.getElementById('id_progresso');
    const statusSelect = document.getElementById('id_status');
    const progressValue = document.getElementById('progress-value');
    
    if (progressInput) {
        // Função para verificar se há imagens
        function hasImages() {
            const mainImageInput = document.getElementById('id_imagem_principal');
            let hasMainImage = mainImageInput && mainImageInput.files && mainImageInput.files.length > 0;
            let hasAdditionalImages = false;
            
            // Verificar imagens adicionais
            const imageInputs = document.querySelectorAll('input[type="file"][name*="imagem"]');
            imageInputs.forEach(input => {
                if (input !== mainImageInput && input.files && input.files.length > 0) {
                    hasAdditionalImages = true;
                }
            });
            
            // Verificar se já existem imagens no relatório (modo edição)
            const existingImages = document.querySelectorAll('.img-thumbnail');
            
            return hasMainImage || hasAdditionalImages || existingImages.length > 0;
        }
        
        // Função para mostrar dicas baseadas em imagens
        function showImageStatusTip() {
            const existingTip = document.querySelector('.image-status-tip');
            if (existingTip) existingTip.remove();
            
            if (hasImages()) {
                const tip = document.createElement('div');
                tip.className = 'alert alert-info alert-dismissible fade show image-status-tip mt-2';
                tip.innerHTML = `
                    <i class="bi bi-lightbulb me-1"></i>
                    <strong>📸 Status Inteligente Ativado:</strong> Como você tem imagens, o status será ajustado automaticamente:
                    <ul class="mb-0 mt-1 small">
                        <li><strong>0% + Fotos:</strong> Em Andamento (documentando problema)</li>
                        <li><strong>1-99% + Fotos:</strong> Em Andamento (trabalhando na solução)</li>
                        <li><strong>100% + Fotos:</strong> Resolvido (trabalho concluído e documentado)</li>
                    </ul>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                statusSelect.parentNode.appendChild(tip);
            }
        }

        // Função para atualizar o display do progresso e status
        function updateProgressAndStatus() {
            const value = parseInt(progressInput.value);
            const hasImagesFlag = hasImages();
            
            // Atualizar o badge com o valor
            if (progressValue) {
                progressValue.textContent = value + '%';
                
                // Atualizar cor do badge baseado no progresso E imagens
                progressValue.className = 'badge ms-2 ';
                
                if (hasImagesFlag) {
                    // Lógica com imagens
                    if (value === 0) {
                        progressValue.className += 'bg-info';
                        progressValue.title = 'Documentando problema';
                    } else if (value < 100) {
                        progressValue.className += 'bg-warning';
                        progressValue.title = 'Trabalhando na solução';
                    } else {
                        progressValue.className += 'bg-success';
                        progressValue.title = 'Trabalho concluído e documentado';
                    }
                } else {
                    // Lógica padrão sem imagens
                    if (value === 0) {
                        progressValue.className += 'bg-secondary';
                        progressValue.title = 'Não iniciado';
                    } else if (value < 100) {
                        progressValue.className += 'bg-warning';
                        progressValue.title = 'Em progresso';
                    } else {
                        progressValue.className += 'bg-success';
                        progressValue.title = 'Concluído';
                    }
                }
            }
            
            // Atualizar status automaticamente baseado no progresso E imagens
            if (statusSelect) {
                if (hasImagesFlag) {
                    // Com imagens: sempre em andamento ou resolvido
                    if (value === 100) {
                        statusSelect.value = 'resolvido';
                    } else {
                        statusSelect.value = 'em_andamento';
                    }
                } else {
                    // Sem imagens: lógica padrão
                    if (value === 0) {
                        statusSelect.value = 'pendente';
                    } else if (value >= 1 && value <= 99) {
                        statusSelect.value = 'em_andamento';
                    } else if (value === 100) {
                        statusSelect.value = 'resolvido';
                    }
                }
                
                // Adicionar feedback visual no select
                statusSelect.className = 'form-select ';
                if (statusSelect.value === 'pendente') {
                    statusSelect.className += 'border-secondary';
                } else if (statusSelect.value === 'em_andamento') {
                    statusSelect.className += 'border-warning';
                } else {
                    statusSelect.className += 'border-success';
                }
            }
            
            // Mostrar dica se necessário
            if (hasImagesFlag) {
                showImageStatusTip();
            }
        }
        
        // Executar ao carregar a página
        updateProgressAndStatus();
        
        // Executar quando o slider muda
        progressInput.addEventListener('input', updateProgressAndStatus);
        
        // Monitorar mudanças em uploads de imagem
        const mainImageInput = document.getElementById('id_imagem_principal');
        if (mainImageInput) {
            mainImageInput.addEventListener('change', function() {
                setTimeout(updateProgressAndStatus, 100); // Pequeno delay para garantir que o arquivo foi processado
            });
        }
        
        // Monitorar imagens adicionais
        document.addEventListener('change', function(e) {
            if (e.target.type === 'file' && e.target.name && e.target.name.includes('imagem')) {
                setTimeout(updateProgressAndStatus, 100);
            }
        });
    }

    // Filtrar equipamentos baseado no local selecionado
    const localSelect = document.getElementById('id_local');
    const equipamentoSelect = document.getElementById('id_equipamento');
    
    if (localSelect && equipamentoSelect) {
        localSelect.addEventListener('change', function() {
            const localId = this.value;
            
            // Limpar opções de equipamento
            equipamentoSelect.innerHTML = '<option value="">Selecione um equipamento</option>';
            
            if (localId) {
                // Buscar equipamentos do local selecionado
                fetch(`/reports/api/equipamentos-por-local/${localId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            data.equipamentos.forEach(eq => {
                                const option = document.createElement('option');
                                option.value = eq.id;
                                option.textContent = `${eq.nome} (${eq.codigo}) - ${eq.tipo}`;
                                equipamentoSelect.appendChild(option);
                            });
                        } else {
                            console.error('Erro ao carregar equipamentos:', data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Erro na requisição:', error);
                    });
            }
        });
    }
});

// Função para definir data/hora atual (será chamada pelo template se necessário)
function setCurrentDateTime() {
    const dataOcorrenciaInput = document.getElementById('id_data_ocorrencia');
    if (dataOcorrenciaInput && !dataOcorrenciaInput.value) {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        dataOcorrenciaInput.value = `${year}-${month}-${day}T${hours}:${minutes}`;
    }
} 