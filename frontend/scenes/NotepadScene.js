class NotepadScene extends Phaser.Scene {
    constructor() {
        super({ key: 'NotepadScene' });
    }

    create(data) {
        const { content } = data;

        const panel = this.add.container(200, 150);
        const background = this.add.graphics();
        background.fillStyle(0x000000, 0.8);
        background.fillRect(0, 0, 600, 400);
        panel.add(background);

        const text = this.add.text(20, 20, content, { fontSize: '16px', fill: '#0f0', wordWrap: { width: 560 } });
        panel.add(text);

        const closeButton = this.add.text(580, 10, 'X', { fontSize: '24px', fill: '#ff0000' }).setOrigin(0.5).setInteractive();
        closeButton.on('pointerdown', () => this.scene.stop());
        panel.add(closeButton);

        this.input.setDraggable(panel);
        panel.on('drag', (pointer, dragX, dragY) => {
            panel.x = dragX;
            panel.y = dragY;
        });
    }
}
