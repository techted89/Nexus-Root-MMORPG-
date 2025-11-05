class ShopScene extends Phaser.Scene {
    constructor() {
        super({ key: 'ShopScene' });
    }

    create() {
        this.add.text(100, 50, 'Hardware Shop', { fontSize: '32px', fill: '#0f0' });

        const backButton = this.add.text(this.cameras.main.width - 150, 50, 'Back to Menu', { fontSize: '24px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        backButton.on('pointerdown', () => {
            this.scene.start('MainMenuScene');
        });

        // Placeholder for shop items
        const shopItems = [
            { name: 'CPU', currentTier: 1, nextTier: 2, price: 100, benefit: '-0.5s on hashcrack' },
            { name: 'RAM', currentTier: 2, nextTier: 3, price: 150, benefit: '+1 concurrent spawn' },
            { name: 'NIC', currentTier: 1, nextTier: 2, price: 120, benefit: '+10% scan speed' }
        ];

        let y = 150;
        shopItems.forEach(item => {
            // Column 1: Current Tier
            this.add.text(100, y, `${item.name} (Tier ${item.currentTier})`, { fontSize: '24px', fill: '#0f0' });

            // Column 2: Next Tier
            this.add.text(400, y, `Upgrade to Tier ${item.nextTier}`, { fontSize: '24px', fill: '#0f0' });
            this.add.text(400, y + 30, `Benefit: ${item.benefit}`, { fontSize: '18px', fill: '#0f0' });

            // Column 3: Price and Buy Button
            this.add.text(700, y, `Price: ${item.price}C`, { fontSize: '24px', fill: '#0f0' });
            const buyButton = this.add.text(700, y + 30, 'Buy', { fontSize: '24px', fill: '#00ff00', backgroundColor: '#050505', padding: { x: 10, y: 5 } })
                .setInteractive();

            buyButton.on('pointerdown', () => {
                this.showBuyConfirmation(item);
            });

            y += 100;
        });
    }

    showBuyConfirmation(item) {
        if (this.confirmationPanel) {
            this.confirmationPanel.destroy();
        }

        const panel = this.add.container(this.cameras.main.width / 2, this.cameras.main.height / 2);
        const background = this.add.graphics();
        background.fillStyle(0x000000, 0.9);
        background.fillRect(-200, -100, 400, 200);
        panel.add(background);

        const title = this.add.text(0, -80, `Confirm Purchase`, { fontSize: '24px', fill: '#0f0' }).setOrigin(0.5);
        panel.add(title);

        const itemText = this.add.text(0, -30, `Upgrade ${item.name} to Tier ${item.nextTier}?`, { fontSize: '18px', fill: '#0f0' }).setOrigin(0.5);
        panel.add(itemText);

        const confirmButton = this.add.text(-50, 50, 'Confirm', { fontSize: '24px', fill: '#00ff00' }).setOrigin(0.5).setInteractive();
        confirmButton.on('pointerdown', () => {
            // In a real implementation, this would send a request to the backend
            console.log(`Purchased ${item.name}`);
            panel.destroy();
        });
        panel.add(confirmButton);

        const cancelButton = this.add.text(50, 50, 'Cancel', { fontSize: '24px', fill: '#ff0000' }).setOrigin(0.5).setInteractive();
        cancelButton.on('pointerdown', () => panel.destroy());
        panel.add(cancelButton);

        this.confirmationPanel = panel;
    }
}
