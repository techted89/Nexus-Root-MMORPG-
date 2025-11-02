class LanScene extends Phaser.Scene {
    constructor() {
        super({ key: 'LanScene' });
    }

    create() {
        this.add.text(100, 50, 'LAN Tree Chart', { fontSize: '32px', fill: '#0f0' });

        this.fetchMissionData('test_user');

        const backButton = this.add.text(this.cameras.main.width - 150, 50, 'Back to Menu', { fontSize: '24px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        backButton.on('pointerdown', () => this.scene.start('MainMenuScene'));
    }

    async fetchMissionData(playerName) {
        try {
            const response = await fetch(`/api/player/${playerName}/missions`);
            const data = await response.json();
            if (data.success) {
                this.renderTree(data.data[0]);
            } else {
                this.add.text(100, 150, `Error: ${data.error}`, { fontSize: '24px', fill: '#ff0000' });
            }
        } catch (error) {
            this.add.text(100, 150, 'Error fetching mission data.', { fontSize: '24px', fill: '#ff0000' });
        }
    }

    renderTree(mission) {
        let y = 150;
        this.add.text(100, y, `Mission: ${mission.title} (${mission.status})`, { fontSize: '24px', fill: '#0f0' });

        mission.objectives.forEach((objective, index) => {
            y += 50;
            this.add.text(150 + index * 50, y, `- ${objective.description} (${objective.status})`, { fontSize: '20px', fill: '#0f0' });
        });
    }
}
