// Função para alternar o formulário de comentário
document.getElementById('commentBtn').addEventListener('click', function() {
    const commentForm = document.getElementById('commentForm');
    commentForm.classList.toggle('active');
});

// Função para abrir o modal com opções para editar ou deletar um comentário
function openOptions(comentarioId) {
    console.log("ID do comentário passado para openOptions:", comentarioId);

    if (!comentarioId) {
        Swal.fire('Erro', 'ID do comentário não encontrado.', 'error');
        return;
    }

    window.selectedCommentId = comentarioId;

    Swal.fire({
        template: '#my-template'
    }).then((result) => {
        if (result.isConfirmed) {
            editComment();
        } else if (result.isDenied) {
            deleteComment();
        }
    });
}

// Função para editar um comentário
function editComment() {
    const comentarioId = window.selectedCommentId;

    Swal.fire({
        title: 'Editar Comentário',
        input: 'text',
        inputLabel: 'Novo conteúdo',
        inputPlaceholder: 'Digite o novo conteúdo do comentário',
        showCancelButton: true,
        confirmButtonText: 'Salvar',
        cancelButtonText: 'Cancelar',
        preConfirm: (novoConteudo) => {
            if (!novoConteudo) {
                Swal.showValidationMessage('O conteúdo não pode estar vazio');
                return false;
            }
            return novoConteudo;
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const novoConteudo = result.value;

            fetch(`/comentarios/editar/${comentarioId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `conteudo=${encodeURIComponent(novoConteudo)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.mensagem) {
                    Swal.fire('Sucesso', data.mensagem, 'success');
                    document.querySelector(`#comentario-${comentarioId} .card-text`).innerText = novoConteudo;
                } else {
                    Swal.fire('Erro', data.erro || 'Erro ao editar o comentário.', 'error');
                }
            })
            .catch(error => {
                Swal.fire('Erro', 'Erro ao processar a solicitação.', 'error');
            });
        }
    });
}

// Função para deletar um comentário
function deleteComment() {
    const comentarioId = window.selectedCommentId;

    if (!comentarioId) {
        Swal.fire('Erro', 'ID do comentário não encontrado.', 'error');
        return;
    }

    Swal.fire({
        title: 'Tem certeza?',
        text: 'Deseja realmente deletar este comentário?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Deletar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/comentarios/deletar/${comentarioId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.mensagem) {
                    Swal.fire('Sucesso', data.mensagem, 'success');
                    document.getElementById(`comentario-${comentarioId}`).remove();
                } else {
                    Swal.fire('Erro', data.erro || 'Erro ao deletar o comentário.', 'error');
                }
            })
            .catch(error => {
                Swal.fire('Erro', 'Erro ao processar a solicitação.', 'error');
            });
        }
    });
}
