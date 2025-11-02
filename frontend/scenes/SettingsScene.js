class SettingsScene extends Phaser.Scene {
    constructor() {
        super({ key: 'SettingsScene' });
    }

    create() {
        this.add.text(100, 50, 'Game Settings', { fontSize: '32px', fill: '#0f0' });

        // UI Layout Setting
        this.add.text(100, 150, 'UI Layout:', { fontSize: '24px', fill: '#0f0' });
        const layoutButton = this.add.text(300, 150, 'Default', { fontSize: '24px', fill: '#0f0' })
            .setInteractive();
        layoutButton.on('pointerdown', () => console.log('Change UI Layout'));

        // Font Size Setting
        this.add.text(100, 250, 'Font Size:', { fontSize: '24px', fill: '#0f0' });
        const fontButton = this.add.text(300, 250, 'Medium', { fontSize: '24px', fill: '#0f0' })
            .setInteractive();
        fontButton.on('pointerdown', () => console.log('Change Font Size'));

        const backButton = this.add.text(this.cameras.main.width - 150, 50, 'Back to Menu', { fontSize: '24px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        backButton.on('pointerdown', () => this.scene.start('MainMenuScene'));
    }
}
