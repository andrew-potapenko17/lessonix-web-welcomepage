function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

window.addEventListener(
    'scroll',
    debounce(() => {
        const scrollY = window.scrollY;
        const body = document.body;
        const aboutSection = document.getElementById('about-section');
        const aboutTitle = document.querySelector('.about-title');
        const aboutText = document.querySelector('.about-text');

        // Toggle background class
        if (scrollY > 150) {
            body.classList.add('scroll-background');
        } else {
            body.classList.remove('scroll-background');
        }

        // Show and animate about section
        if (scrollY >= 210) {
            aboutSection.style.display = 'block';
            aboutSection.style.opacity = '1'; // Fully visible

            // Apply animations only once
            if (!aboutTitle.classList.contains('animate')) {
                aboutTitle.classList.add('animate');
                aboutText.classList.add('animate');
            }
        } else {
            aboutSection.style.display = 'block';
            aboutSection.style.opacity = '0.5'; // Partially visible
            aboutTitle.classList.remove('animate');
            aboutText.classList.remove('animate');
        }
    }, 100) // Wait time of 100 ms
);

const welcomeTitle = document.querySelector('.welcome-title');
const welcomeSubtitle = document.querySelector('.welcome-subtitle');
const toRegister = document.querySelector('.switch');

document.querySelector('.proceed .button').addEventListener('click', function () {
    document.body.classList.add('shrink'); // Apply the class to body or a wrapper element
});

let isRegistering = false;

document.querySelector('.white-square .switch').addEventListener('click', function () {
    const formContainer = document.querySelector('.loginForm .form-container');
    const welcomeTitle = document.querySelector('.welcome-title');
    const welcomeSubtitle = document.querySelector('.welcome-subtitle');
    const toRegister = document.querySelector('.switch');

    // Toggle between login and registration states
    const isRegistering = document.body.classList.toggle('register');

    if (isRegistering) {
        // Switch to registration form
        formContainer.innerHTML = `
            <h2 class="main-heading">Зареєструйтеся до Lessonix</h2>
            <div class="images-container">
                <a href="${facebookAuthUrl}" class="auth-through">
                    <img src="${staticURL}img/facebook-login.png" alt="Facebook" class="small-image">
                </a>
                <a href="${googleAuthUrl}" class="auth-through">
                    <img src="${staticURL}img/google-login.png" alt="Google" class="small-image">
                </a>
                <a href="${twitterAuthUrl }" class="auth-through">
                    <img src="${staticURL}img/x-login.png" alt="X" class="small-image">
                </a>
            </div>
            <p>Або через e-mail:</p>
            <form method="POST" action="${registerAction}">
                <div class="input-group">
                    <img src="${staticURL}img/registerid-ico.png" alt="Register Icon" class="input-icon">
                    <input type="text" name="register_code" placeholder="Реєстраційний код" required />
                </div>
                <div class="input-group">
                    <img src="${staticURL}img/email-ico.png" alt="Email Icon" class="input-icon">
                    <input type="email" name="email" placeholder="E-mail" required />
                </div>
                <div class="input-group">
                    <img src="${staticURL}img/password-ico.png" alt="Password Icon" class="input-icon">
                    <input type="password" name="password" placeholder="Пароль" required />
                </div>
                <div class="input-group">
                    <img src="${staticURL}img/password-ico.png" alt="Confirm Password Icon" class="input-icon">
                    <input type="password" name="confirm_password" placeholder="Підтвердіть пароль" required />
                </div>
                <input type="submit" value="Зареєструватись" class="submit" />
            </form>
        `;
        welcomeTitle.textContent = 'Ласкаво просимо!';
        welcomeSubtitle.textContent = 'Створіть новий обліковий запис';
        toRegister.textContent = 'Вже є обліковий запис?';
    } else {
        // Switch back to login form
        formContainer.innerHTML = `
            <h2 class="main-heading">Увійдіть в акаунт</h2>
            <div class="images-container">
                <a href="${facebookAuthUrl}" class="auth-through">
                    <img src="${staticURL}img/facebook-login.png" alt="Facebook" class="small-image">
                </a>
                <a href="${googleAuthUrl}" class="auth-through">
                    <img src="${staticURL}img/google-login.png" alt="Google" class="small-image">
                </a>
                <a href="${twitterAuthUrl}" class="auth-through">
                    <img src="${staticURL}img/x-login.png" alt="X" class="small-image">
                </a>
            </div>
            <p>Або через e-mail:</p>
            <form method="POST" action="${loginAction}">
                <div class="input-group">
                    <img src="${staticURL}img/email-ico.png" alt="Email Icon" class="input-icon">
                    <input type="email" name="email" placeholder="E-mail" required />
                </div>
                <div class="input-group">
                    <img src="${staticURL}img/password-ico.png" alt="Password Icon" class="input-icon">
                    <input type="password" name="password" placeholder="Пароль" required />
                </div>
                <input type="submit" value="Увійти" class="submit" />
            </form>
        `;
        welcomeTitle.textContent = 'Вітаємо знову!';
        welcomeSubtitle.textContent = 'Введіть дані облікового запису';
        toRegister.textContent = 'Я тут вперше';
    }
});
