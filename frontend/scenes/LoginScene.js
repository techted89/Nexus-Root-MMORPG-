class LoginScene extends Phaser.Scene {
    constructor() {
        super({ key: 'LoginScene' });
    }

    create() {
        this.add.text(100, 100, 'Login', { fontSize: '32px', fill: '#0f0' });

        // Username input
        this.add.text(100, 200, 'Username:', { fontSize: '24px', fill: '#0f0' });
        const usernameInput = this.add.dom(300, 215).createFromHTML('<input type="text" id="username" style="width: 200px; background-color: #000; color: #0f0; border: 1px solid #0f0;">');

        // Password input
        this.add.text(100, 250, 'Password:', { fontSize: '24px', fill: '#0f0' });
        const passwordInput = this.add.dom(300, 265).createFromHTML('<input type="password" id="password" style="width: 200px; background-color: #000; color: #0f0; border: 1px solid #0f0;">');

        // Login button
        const loginButton = this.add.text(300, 320, 'Login', { fontSize: '24px', fill: '#0f0' }).setInteractive();
        loginButton.on('pointerdown', () => {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            this.login(username, password);
        });
    }

    async login(username, password) {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.success) {
            localStorage.setItem('sessionToken', data.token);
            localStorage.setItem('playerName', username);
            this.scene.start('MainMenuScene');
        } else {
            // Handle login error
            this.add.text(300, 400, data.error, { fontSize: '24px', fill: '#ff0000' });
        }
    }
}
