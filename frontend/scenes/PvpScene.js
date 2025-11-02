class PvpScene extends Phaser.Scene {
    constructor() {
        super({ key: 'PvpScene' });
    }

    create() {
        this.add.text(100, 50, '3v3 PvP Battle', { fontSize: '32px', fill: '#0f0' });

        // Placeholder for PvP data
        const pvpData = {
            teamA: [
                { name: 'Player A1', status: 'Online' },
                { name: 'Player A2', status: 'Disabled' },
                { name: 'Player A3', status: 'Online' }
            ],
            teamB: [
                { name: 'Player B1', status: 'Online' },
                { name: 'Player B2', status: 'Online' },
                { name: 'Player B3', status: 'Under Attack' }
            ]
        };

        this.renderPvpTree(pvpData);

        const backButton = this.add.text(this.cameras.main.width - 150, 50, 'Back to Menu', { fontSize: '24px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        backButton.on('pointerdown', () => this.scene.start('MainMenuScene'));
    }

    renderPvpTree(pvpData) {
        let y = 150;
        this.add.text(100, y, 'Team A', { fontSize: '24px', fill: '#0f0' });
        pvpData.teamA.forEach((player, index) => {
            y += 40;
            this.add.text(150, y, `- ${player.name} (${player.status})`, { fontSize: '20px', fill: '#0f0' });
        });

        y += 80;
        this.add.text(100, y, 'Team B', { fontSize: '24px', fill: '#0f0' });
        pvpData.teamB.forEach((player, index) => {
            y += 40;
            this.add.text(150, y, `- ${player.name} (${player.status})`, { fontSize: '20px', fill: '#0f0' });
        });
    }
}
