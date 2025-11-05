class PvpScene extends Phaser.Scene {
    constructor() {
        super({ key: 'PvpScene' });
    }

    create() {
        this.add.text(100, 50, '3v3 PvP Battle', { fontSize: '32px', fill: '#0f0' });

        this.pvpContainer = this.add.container(0, 0);

        const backButton = this.add.text(this.cameras.main.width - 150, 50, 'Back to Menu', { fontSize: '24px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        backButton.on('pointerdown', () => {
            clearInterval(this.pollingInterval);
            this.scene.start('MainMenuScene');
        });

        this.pollingInterval = setInterval(() => this.fetchPvpState(), 3000);
        this.fetchPvpState();
    }

    async fetchPvpState() {
        try {
            const response = await fetch('/api/pvp/state');
            const data = await response.json();
            if (data.success) {
                this.pvpContainer.removeAll(true);
                this.renderPvpTree(data.data);
            }
        } catch (error) {
            console.error('Error fetching PvP state:', error);
        }
    }

    renderPvpTree(pvpData) {
        let y = 150;
        this.pvpContainer.add(this.add.text(100, y, 'Team A', { fontSize: '24px', fill: '#0f0' }));
        pvpData.team_a.forEach((player, index) => {
            y += 40;
            this.pvpContainer.add(this.add.text(150, y, `- ${player.name} (${player.status})`, { fontSize: '20px', fill: '#0f0' }));
        });

        y += 80;
        this.pvpContainer.add(this.add.text(100, y, 'Team B', { fontSize: '24px', fill: '#0f0' }));
        pvpData.team_b.forEach((player, index) => {
            y += 40;
            this.pvpContainer.add(this.add.text(150, y, `- ${player.name} (${player.status})`, { fontSize: '20px', fill: '#0f0' }));
        });
    }
}
