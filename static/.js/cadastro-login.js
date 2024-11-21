// Função para alternar entre o formulário de login e cadastro
function flipForm() {
    const container = document.getElementById('loginCadastro');
    container.classList.toggle('flipped');
}


function togglePasswordVisibility(toggleId, passwordId) {
    const togglePassword = document.getElementById(toggleId);
    const passwordField = document.getElementById(passwordId);

    togglePassword.addEventListener('click', function () {
        const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordField.setAttribute('type', type);
        this.classList.toggle('fa-eye');
        this.classList.toggle('fa-eye-slash');
    });
}

function validarSenha() {
    const password1 = document.getElementById('password1').value;
    const senhaErro = document.getElementById('senhaErro');

    if (password1.length < 4) {
        senhaErro.style.display = 'block';
        return false;  
    } else {
        senhaErro.style.display = 'none';
        return true;  
    }
}

// Aplicando a função de visibilidade da senha
togglePasswordVisibility('togglePassword', 'password');
togglePasswordVisibility('togglePassword1', 'password1');
togglePasswordVisibility('togglePassword2', 'password2');