class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
    }

    create() {
        this.add.text(100, 100, 'Game Scene - LAN Tree Chart Will Go Here', { fontSize: '24px', fill: '#0f0' });

        const backButton = this.add.text(this.cameras.main.width - 150, 50, 'Back to Menu', { fontSize: '24px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        backButton.on('pointerdown', () => this.scene.start('MainMenuScene'));
    }
}
