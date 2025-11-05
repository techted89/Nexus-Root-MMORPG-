class AccountScene extends Phaser.Scene {
    constructor() {
        super({ key: 'AccountScene' });
    }

    create() {
        this.add.text(100, 100, 'Player Account', { fontSize: '32px', fill: '#0f0' });
        this.add.text(100, 200, 'This is where the player account information will be displayed.', { fontSize: '24px', fill: '#0f0' });

        const backButton = this.add.text(this.cameras.main.width - 150, 50, 'Back to Menu', { fontSize: '24px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        backButton.on('pointerdown', () => this.scene.start('MainMenuScene'));
    }
}
