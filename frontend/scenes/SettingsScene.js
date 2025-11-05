class SettingsScene extends Phaser.Scene {
    constructor() {
        super({ key: 'SettingsScene' });
    }

    create() {
        this.add.text(100, 50, 'Game Settings', { fontSize: '32px', fill: '#0f0' });

        // UI Layout Setting
        this.layouts = ['Default', 'Compact', 'Expanded'];
        this.currentLayoutIndex = this.layouts.indexOf(localStorage.getItem('layout') || 'Default');

        this.add.text(100, 150, 'UI Layout:', { fontSize: '24px', fill: '#0f0' });
        const layoutButton = this.add.text(300, 150, this.layouts[this.currentLayoutIndex], { fontSize: '24px', fill: '#0f0' })
            .setInteractive();

        layoutButton.on('pointerdown', () => {
            this.currentLayoutIndex = (this.currentLayoutIndex + 1) % this.layouts.length;
            const newLayout = this.layouts[this.currentLayoutIndex];
            layoutButton.setText(newLayout);
            localStorage.setItem('layout', newLayout);
            // In a real implementation, this would trigger an event to update the UI
        });

        // Font Size Setting
        this.fontSizes = ['Small', 'Medium', 'Large'];
        this.currentFontSizeIndex = this.fontSizes.indexOf(localStorage.getItem('fontSize') || 'Medium');

        this.add.text(100, 250, 'Font Size:', { fontSize: '24px', fill: '#0f0' });
        const fontButton = this.add.text(300, 250, this.fontSizes[this.currentFontSizeIndex], { fontSize: '24px', fill: '#0f0' })
            .setInteractive();

        fontButton.on('pointerdown', () => {
            this.currentFontSizeIndex = (this.currentFontSizeIndex + 1) % this.fontSizes.length;
            const newSize = this.fontSizes[this.currentFontSizeIndex];
            fontButton.setText(newSize);
            localStorage.setItem('fontSize', newSize);
            // In a real implementation, this would trigger an event to update the UI
        });

        const backButton = this.add.text(this.cameras.main.width - 150, 50, 'Back to Menu', { fontSize: '24px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        backButton.on('pointerdown', () => this.scene.start('MainMenuScene'));
    }
}
