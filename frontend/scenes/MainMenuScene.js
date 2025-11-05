class MainMenuScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MainMenuScene' });
    }

    create() {
        this.add.text(this.cameras.main.width / 2, 100, 'NEXUS ROOT', { fontSize: '64px', fill: '#0f0' }).setOrigin(0.5);

        // Player Account Button
        const accountButton = this.add.text(this.cameras.main.width / 2, 300, 'Player Account', { fontSize: '32px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        accountButton.on('pointerdown', () => this.scene.start('AccountScene'));

        // Premium Subscription Button
        const premiumButton = this.add.text(this.cameras.main.width / 2, 400, 'Upgrade to Premium', { fontSize: '32px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        premiumButton.on('pointerdown', () => this.scene.start('PremiumScene'));

        // Settings Button
        const settingsButton = this.add.text(this.cameras.main.width / 2, 500, 'Settings', { fontSize: '32px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        settingsButton.on('pointerdown', () => this.scene.start('SettingsScene'));

        // Start Game Button
        const startButton = this.add.text(this.cameras.main.width / 2, 600, 'View LAN', { fontSize: '32px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        startButton.on('pointerdown', () => this.scene.start('LanScene'));

        // PvP Button
        const pvpButton = this.add.text(this.cameras.main.width / 2, 700, '3v3 PvP Battle', { fontSize: '32px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        pvpButton.on('pointerdown', () => this.scene.start('PvpScene'));
    }
}
